import os 
import cv2
from Fancymages.lib.viz.drawing import Drawer

# -----------------------------------

def retrieve_clipseg_prompts_and_frames(exp_folder):
    
    frames = sorted(os.listdir(exp_folder))
    frames = [f for f in frames if "frame" in f]
    frames = [os.path.join(exp_folder, f) for f in frames]
    
    prompts = [f.split("-")[-1].split(".")[0] for f in frames]
    prompts = list(set(prompts))
    
    new_frames = ["-".join(f.split("-")[:-1]) for f in frames]
    new_frames = list(set(new_frames))

    return new_frames, prompts

# -----------------------------------

def gather_base(folder, base_frame_name, args):
    
    image_path = os.path.join(folder, base_frame_name)

    if not os.path.exists(image_path):
        return None

    img = cv2.imread(image_path)
    
    return [img]

def gather_clipseg(folder, base_frame_name, args):
       
    fname, ext = os.path.splitext(base_frame_name) 
    
    files = os.listdir(folder)
    files = [os.path.join(folder, f) for f in files if fname in f]
    files.sort()
    
    images = [cv2.imread(f) for f in files]
    prompts = [f.split("-")[-1].split(".")[0] for f in files]
        
    drawer = Drawer(None)
    drawer.return_numpy = True
    drawer.default_style()

    images = [drawer.text_anchor(img, text_show = prompts[ind], alignment = "bottom center", font_size = args.font_size)[:,:,:3] for ind, img in enumerate(images)]
    
    return images

def gather_sam(folder, base_frame_name, args):
    
    image_path = os.path.join(folder, base_frame_name)

    if not os.path.exists(image_path):
        return None

    img = cv2.imread(image_path)
    
    return [img]

def gather_mf2(folder, base_frame_name, args):
    
    image_path = os.path.join(folder, base_frame_name)

    if not os.path.exists(image_path):
        return None

    img = cv2.imread(image_path)
    
    return [img]

def gather_mmpose(folder, base_frame_name, args):
    
    image_path = os.path.join(folder, base_frame_name)

    if not os.path.exists(image_path):
        return None

    img = cv2.imread(image_path)
    
    return [img]

def gather_spiga(folder, base_frame_name, args):
    
    image_path = os.path.join(folder, base_frame_name)

    if not os.path.exists(image_path):
        return None

    img = cv2.imread(image_path)
    
    return [img]

def gather_unimatch(folder, base_frame_name, args):
    
    image_path = os.path.join(folder, base_frame_name)

    if not os.path.exists(image_path):
        return None

    img = cv2.imread(image_path)
    
    return [img]


def gather_seem(folder, base_frame_name, args):
       
    fname, ext = os.path.splitext(base_frame_name) 
    
    files = os.listdir(folder)
    files = [os.path.join(folder, f) for f in files if fname in f]
    files.sort()
    
    images = [cv2.imread(f) for f in files]
    prompts = [f.split("-")[-1].split(".")[0] for f in files]
        
    drawer = Drawer(None)
    drawer.return_numpy = True
    drawer.default_style()

    images = [drawer.text_anchor(img, text_show = prompts[ind], alignment = "bottom center", font_size = args.font_size)[:,:,:3] for ind, img in enumerate(images)]
    
    return images

