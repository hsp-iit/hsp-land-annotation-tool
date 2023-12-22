
import torch

from models.clipseg import CLIPDensePredT
from PIL import Image
from torchvision import transforms
from matplotlib import pyplot as plt

import numpy as np
from scipy.io import savemat

import sys
import cv2
import pickle
import os

from lib.utils.VideoDatabase import VideoDatabase

sys.path.append("../clipseg")


class ClipSegWrapper:
    
    def __init__(self):
        
        self.name = "CLIP-Seg"
    
        self.model = CLIPDensePredT(version='ViT-B/16', reduce_dim=64, complex_trans_conv=True)
        self.model.eval();
        
        self.checkpoint = 'weights/rd64-uni-refined.pth'

        # non-strict, because we only stored decoder weights (not CLIP weights)
        self.model.load_state_dict(torch.load(self.checkpoint, map_location=torch.device('cpu')), strict=False);
    
        self.transform = transforms.Compose([
                                                transforms.ToTensor(),
                                                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                                                transforms.Resize((352, 352)),
                                            ])

        self.colormap = plt.get_cmap('viridis')


    def heatmap_from_img(self, image):
                    
        heatmap = (self.colormap(image) * 2**16).astype(np.uint16)[:,:,:3]
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR)

        return heatmap
    
    def process(self, frames, output_folder, output_folder_real, args):
    
        print(f"[PROCESS] Processing with {self.name}...")
            
        for frame in frames:
            
            frame_name, ext = os.path.splitext(os.path.basename(frame))
            
            predictions, masks = self.process_image_text(frame, args.prompts)
            
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
    
    
    def process_image_text(self, image_filename, prompts):
        
        input_image = Image.open(image_filename)
        img = self.transform(input_image).unsqueeze(0)
        
        # predict
        with torch.no_grad():
            preds = self.model(img.repeat(len(prompts),1,1,1), prompts)[0]

        images = [torch.sigmoid(preds[i][0]) for i in range(len(prompts))]        
        heatmaps = [self.heatmap_from_img(img.cpu().numpy()) for img in images]
                    
        return preds, heatmaps
    
    def process_image_image(self, image_filename, image_prompt_filename):
        
        input_image = Image.open(image_filename)
        img = self.transform(input_image).unsqueeze(0)
        
        image_prompt = Image.open(image_prompt_filename)
        image_prompt = self.transform(image_prompt).unsqueeze(0)
        
        # predict
        with torch.no_grad():
            preds = self.model(img, image_prompt)[0]

        img = torch.sigmoid(preds[0][0]) 
        heatmaps = self.heatmap_from_img(img.cpu().numpy())
                    
        return preds, heatmaps
    
    def save_image(self, img, filename, normalize=True):
        
        if normalize:
            cv2.imwrite(filename, img/255.0)    
        else:
            cv2.imwrite(filename, img)
    
    def save_matlab_output(self, prediction, output_path):
        
        savemat(output_path, {'heatmap': prediction[0].cpu().numpy()})

    def save_pickle_output(self, prediction, output_path):
            
        with open(output_path, 'wb') as fp:
            pickle.dump({'heatmap': prediction[0].cpu().numpy()}, fp)
    
    
if __name__ == "__main__":
    
    VDB = VideoDatabase("hsp-land")
    prompts = ['a man\'s face', 'a curtain']
    
    FRAME_ID = 448
    
    frame = VDB.get_frames_for_video("data/videos/DESPICABLEME_eng.mp4")[FRAME_ID]
    
    cseg = ClipSegWrapper()
    
    predictions, masks = cseg.process_image_text(frame, prompts)
    cseg.save_image(masks[0], f"sample_clipseg_{prompts[0]}.jpg")
    cseg.save_matlab_output(predictions[0], f"sample_clipseg_{prompts[0]}.mat")
    
    # frame_prompt = "data/aux/DESPICABLEME_eng_prompt_frame_10_mask_3.jpg"
    # frame_prompt = "data/aux/DESPICABLEME_eng_prompt_frame_10_mask_big_girl.jpg"
    # frame_prompt = "data/aux/DESPICABLEME_eng_prompt_frame_10_mask_man_new.jpg"
    
    # predictions, masks = cseg.process_image_image(frame, frame_prompt)
    # cseg.save_image(masks, f"sample_clipseg_frame_{FRAME_ID+1}.jpg")
        
    