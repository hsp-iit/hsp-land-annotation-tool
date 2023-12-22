import argparse
from lib.viewers import *
from lib.gather_files import *
from lib.utils.VideoDatabase import VideoDatabase
from lib.utils.image_utils import equalize_height_images, pad_images_with_white, pad_images_with_white_vertical, enlarge_image, overlay_gaze_data
from lib.utils.generic_utils import adjust_frames

# -------------------------------------

def decode_format(format):
        
    images = [entry.split(":") for entry in format]
        
    row_ids = list(set([entry[0] for entry in images]))
    row_ids.sort()
    
    return row_ids, images
    
def load_format_from_file(filename):
    
    format_list = list()
    
    with open(filename, "r") as file:
        format_list = file.readlines()

    format_list = [entry.strip() for entry in format_list if len(entry.strip()) > 0]

    return " ".join(format_list)

def group_by_row(row_ids, images):
    
    images_by_row = list()
    
    for index in row_ids:
        entries = [entry[1:] for entry in images if entry[0] == index]
        images_by_row.append(entries)
        
    return images_by_row

def create_visualization(entries_by_row, args):
    
    VDB = VideoDatabase(args.dataset)    
    
    frames = VDB.get_frames_for_video(args.video)
    frames.sort()
    
    gaze_folder = None
    
    # 
    if args.gaze_data not in [None, ""]:
        gaze_folder = VDB.folder_for_video(args.gaze_data, args.video, create=False)
        
        # 
        if not os.path.exists(gaze_folder):
            print(f"[MULTIVIEW] Gaze data folder ({gaze_folder}) specified, but not available!")
            gaze_folder = None
    
    # 
    if args.start is not None:
        info = VDB.load_video_info(args.video)
        frames = adjust_frames(frames, info, args)
    
    images_per_frame = None
    
    output_folder = VDB.folder_for_video(args.output, args.video)
    
    for frame_id, frame in enumerate(frames):
    
        images = list()
        tmp_frame = cv2.imread(frame)
        
        if args.target_height == None:
            args.target_height = tmp_frame.shape[0]
        
        img_gathered = 0

        for row_of_entries in entries_by_row:
            
            current_images = list()
            
            for entry in row_of_entries:
                                              
                input_folder = VDB.folder_for_video(entry[1], args.video)
                base_frame_name = os.path.basename(frame)
                                
                gather_fun = globals()[f'gather_{entry[0]}']
                gathered_images = gather_fun(input_folder, base_frame_name, args)
                
                # print(input_folder, "/", base_frame_name)
                # print(os.path.exists(os.path.join(input_folder, base_frame_name)))
                
                if gathered_images is None or (args.limit is not None and frame_id >= args.limit):
                    break
                
                img_gathered += len(gathered_images)
                        
                current_images += gathered_images
                        
            # equalize height images
            current_images = equalize_height_images(current_images, args.target_height)
            
            # overimpose gaze data on images
            if gaze_folder is not None:
                current_images = [overlay_gaze_data(img, gaze_folder, frame) for img in current_images]
                
            # stack current_images with white padding
            current_images = pad_images_with_white(current_images, padding=args.padding)
            
            # add resulting image to images
            images.append(cv2.hconcat(current_images))
            
        if images_per_frame is None:
            images_per_frame = img_gathered 
        
        if img_gathered < images_per_frame:
            break
                                
        # bring images to same width
        max_width = max([img.shape[1] for img in images])
                
        images = [enlarge_image(img, max_width) for img in images]
        
        # pad images vertically
        images = pad_images_with_white_vertical(images, padding=args.padding)

        # create output filename and save
        img_to_save = cv2.vconcat(images)
        
        out_filename = os.path.join(output_folder, os.path.basename(frame))
        
        cv2.imwrite(out_filename, img_to_save)
        

def main(args):
    
    if args.format_file is not None:
        args.format = load_format_from_file(args.format_file)

    row_indexes, images_meta = decode_format(args.format)
    entries_by_row = group_by_row(row_indexes, images_meta)
    create_visualization(entries_by_row, args)
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Description')
    parser.add_argument('--video', type=str, required=True)
    parser.add_argument('--format', nargs='+', default=[])    
    parser.add_argument('--format_file', type=str, default=None)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--target_height', type=int, default=None)
    parser.add_argument('--start', type=str, default=None)
    parser.add_argument('--limit', type=str, default=None)
    parser.add_argument('--start_frame', type=int, default=None)
    parser.add_argument('--limit_frame', type=int, default=None)
    parser.add_argument('--padding', type=int, default=10)
    parser.add_argument('--font_size', type=int, default=28)    
    parser.add_argument('--gaze_data', type=str, default=None)  
    parser.add_argument('--dataset', type=str, default="hsp-land")           
    args, _ = parser.parse_known_args()
    
    main(args)
