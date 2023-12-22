from PIL import Image
import os
from xdecoder.BaseModel import BaseModel
from xdecoder import build_model

from torchvision import transforms
from detectron2.data.datasets.builtin_meta import COCO_CATEGORIES
from utils.constants import COCO_PANOPTIC_CLASSES

import numpy as np
from utils.distributed import init_distributed
from utils.arguments import load_opt_from_config_files
from utils.visualizer import Visualizer
from xdecoder.language.loss import vl_similarity
import torch 
import cv2

from lib.utils.VideoDatabase import VideoDatabase
import torch.nn.functional as F

from scipy.io import savemat
import pickle

class SEEMWrapper:
    
    def __init__(self):
        
        self.name = "SEEM"
        
        t = []
        t.append(transforms.Resize(512, interpolation=Image.BICUBIC))
        self.transform = transforms.Compose(t)
        self.colors_list = [(np.array(color['color'])/255).tolist() for color in COCO_CATEGORIES] + [[1, 1, 1]]
        
        conf_files = "assets/configs/seem/seem_focall_lang.yaml"        
        
        opt = load_opt_from_config_files(conf_files)
        opt = init_distributed(opt)

        # cur_model = 'None'
        if 'focalt' in conf_files:
            pretrained_pth = os.path.join("weights/seem_focalt_v2.pt")
            if not os.path.exists(pretrained_pth):
                os.system("wget {}".format("https://huggingface.co/xdecoder/SEEM/resolve/main/seem_focalt_v2.pt"))
            # cur_model = 'Focal-T'
        elif 'focal' in conf_files:
            pretrained_pth = os.path.join("weights/seem_focall_v1.pt")
            if not os.path.exists(pretrained_pth):
                os.system("wget {}".format("https://huggingface.co/xdecoder/SEEM/resolve/main/seem_focall_v1.pt"))
            # cur_model = 'Focal-L'

        self.model = BaseModel(opt, build_model(opt)).from_pretrained(pretrained_pth).eval().cuda()
        with torch.no_grad():
            self.model.model.sem_seg_head.predictor.lang_encoder.get_text_embeddings(COCO_PANOPTIC_CLASSES + ["background"], is_eval=True)

        torch.cuda.set_per_process_memory_fraction(0.9, 0)

    
    @torch.no_grad()
    def process_image(self, image_filename, prompts):
        
        input_image = Image.open(image_filename)
        
        all_masks = list()
        binary_masks = list()
        
        for reftxt in prompts:
                    
            image_ori = self.transform(input_image)
            width = image_ori.size[0]
            height = image_ori.size[1]
            image_ori = np.asarray(image_ori)
            visual = Visualizer(image_ori, metadata=None)
            images = torch.from_numpy(image_ori.copy()).permute(2,0,1).cuda()

            data = {"image": images, "height": height, "width": width}
            
            # inistalize task
            self.model.model.task_switch['spatial'] = False
            self.model.model.task_switch['visual'] = False
            self.model.model.task_switch['grounding'] = True
            self.model.model.task_switch['audio'] = False

            text = None
            
            self.model.model.task_switch['grounding'] = True
            data['text'] = [reftxt]

            torch.cuda.empty_cache() 

            batch_inputs = [data]
            results,image_size,extra = self.model.model.evaluate_demo(batch_inputs)
            
            pred_masks = results['pred_masks'][0]
            v_emb = results['pred_captions'][0]
            t_emb = extra['grounding_class']

            t_emb = t_emb / (t_emb.norm(dim=-1, keepdim=True) + 1e-7)
            v_emb = v_emb / (v_emb.norm(dim=-1, keepdim=True) + 1e-7)

            temperature = self.model.model.sem_seg_head.predictor.lang_encoder.logit_scale
            out_prob = vl_similarity(v_emb, t_emb, temperature=temperature)
            
            matched_id = out_prob.max(0)[1]
            pred_masks_pos = pred_masks[matched_id,:,:]
            pred_class = results['pred_logits'][0][matched_id].max(dim=-1)[1]

            # interpolate mask to ori size
            pred_masks_pos = (F.interpolate(pred_masks_pos[None,], image_size[-2:], mode='bilinear')[0,:,:data['height'],:data['width']] > 0.0).float().cpu().numpy()

            for _, mask in enumerate(pred_masks_pos):
                demo = visual.draw_binary_mask(mask, color=self.colors_list[pred_class[0]%133], text=reftxt)
                cur_binary_mask = mask
                
            res = demo.get_image()
            torch.cuda.empty_cache()
            
            binary_masks.append(cur_binary_mask)
            all_masks.append(res)
            
        return binary_masks, all_masks     
        
    def process(self, frames, output_folder, output_folder_real, args):

        print(f"[PROCESS] Processing with {self.name}...")
            
        for frame in frames:
            
            frame_name, ext = os.path.splitext(os.path.basename(frame))
            
            predictions, masks = self.process_image(frame, args.prompts)
            
            for index, (prompt, mask) in enumerate(zip(args.prompts, masks)):
                
                output_name = os.path.join(output_folder, f"{frame_name}-{prompt}{ext}")
                self.save_image(mask, output_name)    
        
                if output_folder_real is not None:
                    
                    if args.save_mat:
                            
                            output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}-{prompt}.mat")                
                            self.save_matlab_output(predictions[index], output_name_mat)
            
                    else:
        
                            output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}-{prompt}.pkl")                
                            self.save_pickle_output(predictions[index], output_name_pkl)

        
        print(f"[PROCESS] Processed a total of {args.limit} frames.")
        print()
    
    
    def save_image(self, mask, output_name):
        
        cv2.imwrite(output_name, cv2.cvtColor(mask, cv2.COLOR_BGR2RGB))        
    
    def save_matlab_output(self, prediction, output_path):
        
        savemat(output_path, {'mask': prediction.astype(np.uint8)})
    
    def save_pickle_output(self, prediction, output_path):
                        
        with open(output_path, 'wb') as fp:
            pickle.dump({'mask': prediction.astype(np.uint8)}, fp)
        
    
        
if __name__ == "__main__":
    
    VDB = VideoDatabase("hsp-land")
    prompts = ['man', 'curtains']
    
    frame = VDB.get_frames_for_video("data/videos/DESPICABLEME_eng.mp4")[10]
    
    seem = SEEMWrapper()
            
    predictions, masks = seem.process_image(frame, prompts)
    seem.save_image(masks[0], f"sample_seem_{prompts[0]}.jpg")
    seem.save_image(masks[1], f"sample_seem_{prompts[1]}.jpg")
    
    seem.save_matlab_output(predictions[0], f"sample_seem_{prompts[0]}.mat")
