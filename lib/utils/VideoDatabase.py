
import json
import os
import cv2

class VideoDatabase:
    
    def __init__(self, database_name, filename = None):
        
        self.db_name = database_name
        
        if filename is None:
            filename = f"{database_name}.json"
        
        self.filename = filename
        self.video_dict = dict()
        
        self.db_folder_path = os.path.join("data", self.db_name)
        
        if os.path.exists(self.db_folder_path):
            print(f"[VDB] while initializing DB, folder {self.db_folder_path} exists!")
        else:
            os.makedirs(self.db_folder_path)
            
        self.db_file_path = os.path.join("data", "databases", self.filename)
            
        if os.path.exists(os.path.join(self.db_file_path)):
            self.load()
    
    def load(self):
        
        with open(self.db_file_path, "r") as f:
            self.video_dict = json.load(f)
        
    def save(self):
        
        with open(self.db_file_path, "w") as f:
            json_string = json.dumps(self.video_dict)
            f.write(json_string)
            
    def video_id_by_name(self, videoname):
        
        for k,v in self.video_dict.items():
            if videoname == v["name"]:
                return k, True, v
                        
        return None, False, None
    
    def folder_for_video(self, foldername, videoname, simplify = False, create = True):
        
        if simplify:
            videoname = os.path.basename(videoname)        
        
        video_id, found, _ = self.video_id_by_name(videoname)        
        
        if not found:
            print(f"[VDB] Can't create subfolder for {videoname}, video not found!")
            return None
        
        folder_path = os.path.join(self.db_folder_path, str(video_id), foldername)
                
        if create:
            os.makedirs(folder_path, exist_ok=True)

        return folder_path
    
    def get_video_fps(self, videoname):
        
        cap = cv2.VideoCapture(videoname)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        return round(fps)
    
    def add_video(self, videoname, simplify = False, create = True):
        
        if simplify:
            videoname = os.path.basename(videoname)
        
        video_id, found, _ = self.video_id_by_name(videoname)        

        if found:
            print(f"[VDB] Not adding video {videoname}, found at key {video_id}!")
            return
        
        keys = list(self.video_dict.keys())
        keys.sort()
        
        if len(keys) > 0:
            new_key = str(int(keys[-1])+1)    
        else:
            new_key = str(1)
        
        self.video_dict[new_key] = {"name": videoname, 
                                    "fps": self.get_video_fps(videoname)}
        
        new_folder_path = os.path.join(self.db_folder_path, new_key)
        
        if create:
            os.makedirs(new_folder_path, exist_ok=True)
            
            print(f"[VDB] Converting video...")
            self.video_to_frames(videoname)            
            print(f"[VDB] Video {videoname} converted to frames!")
        
        return new_key, new_folder_path
    
    def video_to_frames(self, original_videoname, simplify = False):
        
        if simplify:
            videoname = os.path.basename(videoname)        
        else:
            videoname = original_videoname        
                
        images_folder = self.folder_for_video("images", videoname)
        
        cap = cv2.VideoCapture(original_videoname)

        # first frame read
        _, frame = cap.read()

        # dumped frame number
        incr_id = 1

        while frame is not None:
                
            output_imgfile = os.path.join(images_folder, f"frame-{incr_id:06d}.jpg")
            cv2.imwrite(output_imgfile, frame)
            
            incr_id += 1

            # get next frame available
            _, frame = cap.read()

        print("[VDB] Video Processing Completed.\n")
        
    def load_video_info(self, videoname):
        
        _, found, video_info = self.video_id_by_name(videoname)
        
        if found is None:
            print(f"[VDB] Video {videoname} not found, cannot return video info!")
            return            
        
        return video_info
        
    def get_frames_for_video(self, videoname, subsample = 1, simplify = False):
        
        if simplify:
            videoname = os.path.basename(videoname)        
                
        images_folder = self.folder_for_video("images", videoname)
        
        images_files = os.listdir(images_folder)
        images_files.sort()
        
        # heuristic: getting fifth filename to extract the images extension
        filetype = os.path.splitext(images_files[5])[1].replace(".", "")
        images_files = [os.path.join(images_folder, img) for img in images_files if img.endswith(filetype)]
        
        return images_files[0::subsample]
        
    def show_content(self):
        
        print(f"[VDB] Contents for the {self.db_name} database:")
        for (k,v) in self.video_dict.items():
            print(f"{k}: {v}")      
            
    def list_videos_names(self):
        
        return list(self.video_dict.values())
    