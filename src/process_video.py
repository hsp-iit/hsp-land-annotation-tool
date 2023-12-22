import argparse

from lib.utils.VideoDatabase import VideoDatabase
from lib.processors import *
from lib.utils.generic_utils import adjust_frames
from lib.wrappers import ClipSegWrapper, SPIGAWrapper, Mask2FormerWrapper, MMPoseWrapper, SEEMWrapper, UniMatchWrapper
    
available_methods = {'clipseg': ClipSegWrapper.ClipSegWrapper,
                     'spiga': SPIGAWrapper.SPIGAWrapper,
                     'mf2': Mask2FormerWrapper.Mask2FormerWrapper,
                     'seem': SEEMWrapper.SEEMWrapper,
                     'unimatch': UniMatchWrapper.UniMatchWrapper,
                     'mmpose': MMPoseWrapper.MMPoseWrapper}

# --------------------------------------------------------------------

def fix_args_format(args):
    
    args.prompts = args.prompts.split("' '")
    args.prompts = [p.replace("'", "") for p in args.prompts]
    return args

def initialize_method(method):

    if method not in available_methods.keys():
        print(f"[PROCESS] Can't initialize model, method {method} not found in {available_methods}")
        print()
        return None

    return available_methods[args.method]()

def main(args):
    
    model  = initialize_method(args.method)
    VDB    = VideoDatabase(args.dataset)
    frames = VDB.get_frames_for_video(args.video)
    info   = VDB.load_video_info(args.video)
    
    if frames is None:
        print("[PROCESS] Error processing video - frames set to None (video not found?)")
        print()
        return
    
    out_folder = VDB.folder_for_video(args.output, args.video)
    out_folder_real = VDB.folder_for_video(args.output_real, args.video) if args.output_real is not None else None
    
    frames = adjust_frames(frames, info, args)        
    model.process(frames, out_folder, out_folder_real, args)

# --------------------------------------------------------------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('--video', type=str, required=True)
    parser.add_argument('--method', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--output_real', type=str, default=None)
    parser.add_argument('--start', type=str, default=None)
    parser.add_argument('--limit', type=str, default=None)
    parser.add_argument('--start_frame', type=int, default=None)
    parser.add_argument('--limit_frame', type=int, default=None)
    parser.add_argument('--dataset', type=str, default="hsp-land") 
    parser.add_argument('--prompts', type=str, default="") 
    parser.add_argument('--save_mat', action='store_true')
    args, _ = parser.parse_known_args()
    
    # TODO: fix this workaround for the prompts propagation
    args = fix_args_format(args)
        
    main(args)
