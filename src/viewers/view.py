import argparse
from lib.viewers import *
from lib.utils.VideoDatabase import VideoDatabase

available_methods = ['clipseg', 'sam', 'spiga', 'mf2', 'mmpose']

# -------------------------------------

def initialize_method(method):

    if method not in available_methods:
        print(f"[VIEWER] Can't start visualization, method {method} not found in {available_methods}")
        print()
        return None

    return globals()[f"visualize_{args.method}"]

def main(args):
    
    VDB = VideoDatabase("hsp-land")
    frames = VDB.get_frames_for_video(args.video)
    exp_folder = VDB.folder_for_video(args.folder, args.video)
    visualization_folder = VDB.folder_for_video(args.output, args.video)

    visualizer = initialize_method(args.method)
    visualizer(frames, exp_folder, visualization_folder, args)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('--video', type=str, required=True)
    parser.add_argument('--method', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--folder', type=str, required=True)
    parser.add_argument('--font_size', type=int, default=28)    
    args, _ = parser.parse_known_args()
    
    main(args)
