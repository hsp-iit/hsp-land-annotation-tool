
import numpy as np
from lib.utils.VideoDatabase import VideoDatabase
import torch.nn.functional as F

from unimatch.unimatch import UniMatch
from lib.utils.flow_viz import save_vis_flow_tofile, get_vis_flow
from assets.configs.unimatch.config import get_unimatch_args
import cv2
import torch
from PIL import Image
from os.path import *
from scipy.io import savemat

import pickle 
import os

class InputPadder:
    """ Pads images such that dimensions are divisible by 8 """

    def __init__(self, dims, mode='sintel', padding_factor=8):
        
        self.ht, self.wd = dims[-2:]
        pad_ht = (((self.ht // padding_factor) + 1) * padding_factor - self.ht) % padding_factor
        pad_wd = (((self.wd // padding_factor) + 1) * padding_factor - self.wd) % padding_factor
        if mode == 'sintel':
            self._pad = [pad_wd // 2, pad_wd - pad_wd // 2, pad_ht // 2, pad_ht - pad_ht // 2]
        else:
            self._pad = [pad_wd // 2, pad_wd - pad_wd // 2, 0, pad_ht]

    def pad(self, *inputs):
        return [F.pad(x, self._pad, mode='replicate') for x in inputs]

    def unpad(self, x):
        ht, wd = x.shape[-2:]
        c = [self._pad[2], ht - self._pad[3], self._pad[0], wd - self._pad[1]]
        return x[..., c[0]:c[1], c[2]:c[3]]
    
class UniMatchWrapper:
    
    def __init__(self):
        
        self.name = "UniMatch"      
        
        self.args = get_unimatch_args()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        self.model = UniMatch(feature_channels=self.args["feature_channels"],
                    num_scales=self.args["num_scales"],
                    upsample_factor=self.args["upsample_factor"],
                    num_head=self.args["num_head"],
                    ffn_dim_expansion=self.args["ffn_dim_expansion"],
                    num_transformer_layers=self.args["num_transformer_layers"],
                    reg_refine=self.args["reg_refine"],
                    task=self.args["task"]).to(self.device)
        
        if self.args["resume"]:
            # print('Load checkpoint: %s' % self.args["resume"])
            # loc = 'cuda:{}'.format(self.args["local_rank"]) if torch.cuda.is_available() else 'cpu'
            checkpoint = torch.load(self.args["resume"], map_location=self.device)

            self.model.load_state_dict(checkpoint['model'], strict=self.args["strict_resume"])
        
        torch.cuda.set_per_process_memory_fraction(0.9, 0)

    
    def process(self, frames, output_folder, output_folder_real, args):
    
        print(f"[PROCESS] Processing with {self.name}...")
            
        for frame1, frame2 in zip(frames[:-1], frames[1:]):
            
            frame_name, ext = os.path.splitext(os.path.basename(frame1))
            
            prediction, flow_img = self.process_images(frame1, frame2, args)
            output_name = os.path.join(output_folder, f"{frame_name}{ext}")
            
            self.save_image(flow_img, output_name)
                
            if output_folder_real is not None:
                
                if args.save_mat:
                
                    output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.mat")
                    self.save_matlab_output(prediction, output_name_mat)
            
                else:
                    
                    output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.pkl")
                    self.save_pickle_output(prediction, output_name_pkl)
                            

        print(f"[PROCESS] Processed a total of {args.limit} frames.")
        print()
    
    
    def max_resize(self, img, maxwidth=1024, maxheight=1024):
    
        f1 = maxwidth / img.shape[1]
        f2 = maxheight / img.shape[0]
        f = min(f1, f2)  # resizing factor
        dim = (int(img.shape[1] * f), int(img.shape[0] * f))
        resized = cv2.resize(img, dim)
        
        return resized

    @torch.no_grad()
    def process_images(self, image1, image2, args = None):

        image1 = Image.open(image1)
        image2 = Image.open(image2)        
        
        image1 = np.array(image1).astype(np.uint8)[..., :3]
        image2 = np.array(image2).astype(np.uint8)[..., :3]
        
        image1 = self.max_resize(image1)
        image2 = self.max_resize(image2)

        image1 = torch.from_numpy(image1).permute(2, 0, 1).float().to(self.device)
        image2 = torch.from_numpy(image2).permute(2, 0, 1).float().to(self.device)

        image1 = image1[None]
        image2 = image2[None]
        
        torch.cuda.empty_cache() 
        
        nearest_size = [int(np.ceil(image1.size(-2) / self.args["padding_factor"])) * self.args["padding_factor"],
                        int(np.ceil(image1.size(-1) / self.args["padding_factor"])) * self.args["padding_factor"]]

        # resize to nearest size or specified size
        inference_size = nearest_size #if fixed_inference_size is None else fixed_inference_size

        assert isinstance(inference_size, list) or isinstance(inference_size, tuple)
        ori_size = image1.shape[-2:]

        # resize before inference
        if inference_size[0] != ori_size[0] or inference_size[1] != ori_size[1]:
            image1 = F.interpolate(image1, size=inference_size, mode='bilinear',
                                   align_corners=True)
            image2 = F.interpolate(image2, size=inference_size, mode='bilinear',
                                   align_corners=True)
        
        padder = InputPadder(image1.shape, padding_factor=self.args["padding_factor"])
        image1, image2 = padder.pad(image1, image2)

        results_dict = self.model(image1, image2,
                                attn_type=self.args["attn_type"],
                                attn_splits_list=self.args["attn_splits_list"],
                                corr_radius_list=self.args["corr_radius_list"],
                                prop_radius_list=self.args["prop_radius_list"],
                                num_reg_refine=self.args["num_reg_refine"],
                                task='flow',
                                )

        flow_preds = results_dict['flow_preds'][-1]
        flow = padder.unpad(flow_preds[0]).permute(1, 2, 0).cpu().numpy()
                
        return flow, get_vis_flow(flow)

    def save_image(self, img, output):
        
        cv2.imwrite(output, img)        

    def save_flow_to_file(self, flow, filename):
        
        save_vis_flow_tofile(flow, filename)
        
    def save_matlab_output(self, predictions, output_path):
        
        savemat(output_path, {'flow': predictions})

    def save_pickle_output(self, predictions, output_path):
        
        with open(output_path, 'wb') as fp:
            pickle.dump({'flow': predictions}, fp)

    
if __name__ == "__main__":
    
    VDB = VideoDatabase("hsp-land")
    frames = VDB.get_frames_for_video("data/videos/DESPICABLEME_eng.mp4")[15:20]
    
    model = UniMatchWrapper()
    
    prediction, visualization_output = model.process_images(frames[0], frames[1])
    model.save_image(visualization_output, "unimatch_sample.jpg")
    
    model.save_matlab_output(prediction, "unimatch_sample.mat")