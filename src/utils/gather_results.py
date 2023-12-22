import argparse
import os 
    
from lib.utils.VideoDatabase import VideoDatabase

# ----------------------------------------

def main(args):
    
    if len(args.folders) == 0:
        print("[GATHER] Please provide at least one folder to zip.")
        print()
        return      
    
    VDB = VideoDatabase(args.dataset)
    frames = VDB.get_frames_for_video(args.video)
    
    if frames is None:
        print("[GATHER] Error processing video - frames set to None (video not found?)")
        print()
        return
    
    all_folders = list()
    
    for folder in args.folders:
    
        out_folder = VDB.folder_for_video(folder, args.video)
        all_folders.append(out_folder)
    
    all_folders = " ".join(all_folders)
    cmd = f"zip -q -r {args.output} {all_folders}"
    print(f"[GATHER] Running command: {cmd}")    
    os.system(cmd)
    
# ----------------------------------------

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('--video', type=str, required=True)
    parser.add_argument('--folders', nargs='+', default=[])    
    parser.add_argument('--dataset', type=str, default="hsp-land")     
    parser.add_argument('--output', type=str, required=True)
    args, _ = parser.parse_known_args()
    
    main(args)
