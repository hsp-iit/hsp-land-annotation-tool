
import os
import cv2
from Fancymages.lib.viz.drawing import Drawer

from lib.utils.image_utils import load_images_and_equalize_height, pad_images_with_white


# ------------------------------------------------
# CLIP-Seg part

def retrieve_clipseg_prompts_and_frames(exp_folder):
    
    frames = sorted(os.listdir(exp_folder))
    frames = [f for f in frames if "frame" in f]
    frames = [os.path.join(exp_folder, f) for f in frames]
    
    prompts = [f.split("-")[-1].split(".")[0] for f in frames]
    prompts = list(set(prompts))
    
    new_frames = ["-".join(f.split("-")[:-1]) for f in frames]
    new_frames = list(set(new_frames))

    return new_frames, prompts

def visualize_clipseg(frames, exp_folder, visualization_folder, args):
      
    exp_frames, prompts = retrieve_clipseg_prompts_and_frames(exp_folder)
        
    drawer = Drawer(None)
    drawer.return_numpy = True
    drawer.default_style()
    
    for frame, exp_frame in zip(frames, exp_frames):

        exp_frame_currents = [f"{exp_frame}-{p}.jpg" for p in prompts]
        frame_img, result_images = load_images_and_equalize_height(frame, exp_frame_currents)
                
        for index, prompt in enumerate(prompts):
            result_images[index] = drawer.text_anchor(result_images[index], text_show = prompt, alignment = "bottom center", font_size = args.font_size)[:,:,:3]
                        
        all_images = pad_images_with_white([frame_img] + result_images)
        concat_img = cv2.hconcat(all_images)
        
        out_filename = os.path.join(visualization_folder, os.path.basename(frame))
        
        cv2.imwrite(out_filename, concat_img)
        
        
# ------------------------------------------------
# Segment-Anything part
        
def retrieve_frames(exp_folder):
    
    frames = sorted(os.listdir(exp_folder))
    frames = [f for f in frames if "frame" in f]
    frames = [os.path.join(exp_folder, f) for f in frames]
    
    return frames

def visualize_sam(frames, exp_folder, visualization_folder, args):
      
    exp_frames = retrieve_frames(exp_folder)
            
    for frame, exp_frame in zip(frames, exp_frames):

        frame_img, result_images = load_images_and_equalize_height(frame, [exp_frame])
                                        
        all_images = pad_images_with_white([frame_img] + result_images)
        concat_img = cv2.hconcat(all_images)
        
        out_filename = os.path.join(visualization_folder, os.path.basename(frame))
        
        cv2.imwrite(out_filename, concat_img)
    
# ------------------------------------------------
        
def visualize_spiga(frames, exp_folder, visualization_folder, args):
      
    exp_frames = retrieve_frames(exp_folder)
            
    for frame, exp_frame in zip(frames, exp_frames):

        frame_img, result_images = load_images_and_equalize_height(frame, [exp_frame])
                                        
        all_images = pad_images_with_white([frame_img] + result_images)
        concat_img = cv2.hconcat(all_images)
        
        out_filename = os.path.join(visualization_folder, os.path.basename(frame))
        
        cv2.imwrite(out_filename, concat_img)
    
# ------------------------------------------------
        
def visualize_mf2(frames, exp_folder, visualization_folder, args):
      
    exp_frames = retrieve_frames(exp_folder)
            
    for frame, exp_frame in zip(frames, exp_frames):

        frame_img, result_images = load_images_and_equalize_height(frame, [exp_frame])
                                        
        all_images = pad_images_with_white([frame_img] + result_images)
        concat_img = cv2.hconcat(all_images)
        
        out_filename = os.path.join(visualization_folder, os.path.basename(frame))
        
        cv2.imwrite(out_filename, concat_img)
        
# ------------------------------------------------

def visualize_mmpose(frames, exp_folder, visualization_folder, args):
      
    exp_frames = retrieve_frames(exp_folder)
            
    for frame, exp_frame in zip(frames, exp_frames):

        frame_img, result_images = load_images_and_equalize_height(frame, [exp_frame])
                                        
        all_images = pad_images_with_white([frame_img] + result_images)
        concat_img = cv2.hconcat(all_images)
        
        out_filename = os.path.join(visualization_folder, os.path.basename(frame))
        
        cv2.imwrite(out_filename, concat_img)
                