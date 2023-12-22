
from lib.utils.VideoDatabase import VideoDatabase
import argparse
import os 

# ----------------------------------------

def create_dataset(args):
    
    files = os.listdir(args.folder)
    files.sort()
    full_filenames = [os.path.join(args.folder, f) for f in files]
    
    VDB = VideoDatabase(args.dataset)    

    for video_filename in full_filenames:
        VDB.add_video(video_filename)

    VDB.save()
    
    print(f"-- Created dataset {args.dataset} with {len(full_filenames)} videos!")

# ----------------------------------------
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('--folder', type=str, required=True)
    parser.add_argument('--dataset', type=str, default="hsp-land")
    args, _ = parser.parse_known_args()
    
    create_dataset(args)