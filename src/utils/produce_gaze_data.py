import os
import argparse
from math import cos, sin, pi

from lib.utils.VideoDatabase import VideoDatabase
from pathlib import Path
        
def produce_gaze_files(images_folder, gaze_folder):
    
    files = os.listdir(images_folder)
    files.sort()

    for f in files:
        
        base, _ = os.path.splitext(f)
        full_gaze_filename = os.path.join(gaze_folder, f"{base}.txt")
        Path(full_gaze_filename).touch()

        
def main(args):      
        
    VDB    = VideoDatabase("hsp-land")
    info   = VDB.load_video_info(args.video)
    fps = info["fps"]
    
    images_folder = VDB.folder_for_video("images", args.video)
    folder = VDB.folder_for_video(args.output, args.video)
    
    produce_gaze_files(images_folder, folder)

    all_files = os.listdir(folder)
    all_files.sort()

    radius = 0.3

    for f in all_files:

        base, _ = os.path.splitext(f)
        t = int(base.split("-")[1])
        
        moment = ((2*pi)/(fps*args.period))*t
        x = cos(moment) * radius + 0.5
        y = sin(moment) * radius + 0.5
        
        x2 = sin(moment) * radius * 1.2 + 0.5
        y2 = - sin(2*moment) * radius * 0.8 + 0.5
            
        with open(os.path.join(folder, f), "w") as writefile:
            writefile.writelines(f"{x},{y},{3}\n")
            writefile.writelines(f"{x2},{y2},{5}\n")
            
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('--video', type=str, required=True)
    parser.add_argument('--output', type=str, default="gaze")
    parser.add_argument('--period', type=int, default=4)    
    args, _ = parser.parse_known_args()
    
    main(args)
