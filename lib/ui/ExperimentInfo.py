
import os
from pathlib import Path
import re 

class ExperimentInfo(object):

    def __init__(self, folder):

        self.results_folder = folder
        self.base_folder = str(Path(folder).parent)
        self.images_folder = os.path.join(self.base_folder, "images")

        self.images = self.get_images()
        self.methods, self.methods_folders = self.get_available_methods()
        
        self.prompts = self.get_available_prompts()

        
    def set_pickle_folder(self, folder):
        
        self.pickle_base_folder = folder    
        self.pickle_folders = [os.path.join(self.pickle_base_folder, f) for f in self.methods]
        
        
    def get_images(self, start=0, end=None):
        
        all_images = os.listdir(self.images_folder)
        all_images.sort()
        all_images = [os.path.join(self.images_folder, f) for f in all_images]
        
        if end is None:
            return all_images[start:]
        else:
            return all_images[start:end+1]
           
            
    def get_available_methods(self):
        
        folders = os.listdir(self.results_folder)
        folders.sort()
        
        all_folders = [os.path.join(self.results_folder, f) for f in folders]
        
        return folders, all_folders
    
    
    def get_image(self, index):
        
        return self.images[max(min(index, len(self.images)-1), 0)]
    
    
    def get_image_from_result_path(self, result_path):
        
        numbers = re.findall(r'-(\d{6})', result_path)[0]
        res = [i for i in self.images if numbers in i]
        return res[0]


    def get_image_index_from_name(self, image_name):
        
        pass
    
    
    def get_actual_images_number(self):
        
        method_folder = os.path.join(self.results_folder, "mf2")
        all_images = os.listdir(method_folder)
        return len(all_images)
    
    
    def get_image_for_method(self, index, method, prompt = None):
        
        if method in ["clipseg", "seem"]:
            
            method_folder = os.path.join(self.results_folder, method)
            
            all_images = os.listdir(method_folder)
            all_images = [im for im in all_images if prompt in im]
            all_images.sort()
            all_images = [os.path.join(method_folder, f) for f in all_images]
        
            if index >= len(all_images):
                return None
            else:
                return all_images[index]
        
        else:
        
            method_folder = os.path.join(self.results_folder, method)
            
            all_images = os.listdir(method_folder)
            all_images.sort()
            all_images = [os.path.join(method_folder, f) for f in all_images]
            
            if index >= len(all_images):
                return None
            else:
                return all_images[index]
            
        
    def num_images(self):
        
        return len(self.images)
    
    
    def get_available_prompts(self):
        
        available = [m for m in ["clipseg", "seem"] if m in self.methods]
        
        if len(available) == 0:
            return list()
        
        available = available[0]
                
        method_dir = os.path.join(self.results_folder, available)
        files = os.listdir(method_dir)
        suffixes = [f.split("-")[-1].split(".")[0] for f in files]
                
        return list(set(suffixes))
    
    
    def load_all_data(self):
        
        print()
        print("[EXPI] DEBUG")
        print(self.results_folder)        
        print(self.base_folder)        
        print(self.images_folder)        
        print(self.methods)        
        print(self.pickle_base_folder)
        print(self.pickle_folders)        
        print(self.prompts)        
        print()