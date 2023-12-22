
import argparse

from lib.utils.VideoDatabase import VideoDatabase

import argparse
import multiprocessing as mp

from detectron2.config import get_cfg
from detectron2.data.detection_utils import read_image
from detectron2.projects.deeplab import add_deeplab_config
from detectron2.utils.logger import setup_logger
from detectron2.data.datasets.builtin_meta import COCO_CATEGORIES

from mask2former import add_maskformer2_config
from predictor import VisualizationDemo
from scipy.io import savemat
import numpy as np
import os 
import pickle

class Mask2FormerWrapper:
    
    def __init__(self):

        self.name = "Mask2Former"

        mp.set_start_method("spawn", force=True)

        self.args = self.get_parser().parse_known_args()

        setup_logger(name="fvcore")
        
        self.logger = setup_logger()
        self.logger.info("Arguments: " + str(self.args))

        self.cfg = self.setup_cfg(self.args)
        self.model = VisualizationDemo(self.cfg)
        
    def process_image(self, image_path):
        
        img = read_image(image_path, format="BGR")
        prediction, visualized_output = self.model.run_on_image(img)      
        
        return prediction, visualized_output

    def process(self, frames, output_folder, output_folder_real, args):

        print(f"[PROCESS] Processing with {self.name}...")
            
        for frame in frames:
            
            frame_name = os.path.basename(frame)
            output_name = os.path.join(output_folder, frame_name)
                    
            prediction, vis_output = self.process_image(frame)
            self.save_image(vis_output, output_name)
            
            if output_folder_real is not None:
                
                if args.save_mat:

                    output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.mat")
                    self.save_matlab_output(prediction, output_name_mat)
            
                else:        

                    output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.pkl")
                    self.save_pickle_output(prediction, output_name_pkl)
        
        print(f"[PROCESS] Processed a total of {args.limit} frames.")
        print()

        
    def save_image(self, visualized_output, output_path):
        
        visualized_output.save(output_path)
        
    def save_matlab_output(self, predictions, output_path):
        
        panoptic_mask, instance_infos = predictions['panoptic_seg']
        classes = [COCO_CATEGORIES[inst['category_id']]['name'] for inst in instance_infos]
        
        savemat(output_path, {'masks': np.array(panoptic_mask.cpu().numpy().astype(np.uint8)), 'classes': classes})
        
    def save_pickle_output(self, predictions, output_path):
            
        panoptic_mask, instance_infos = predictions['panoptic_seg']
        classes = [COCO_CATEGORIES[inst['category_id']]['name'] for inst in instance_infos]            
            
        with open(output_path, 'wb') as fp:
            pickle.dump({'masks': np.array(panoptic_mask.cpu().numpy().astype(np.uint8)), 'classes': classes}, fp)
        

    def setup_cfg(self, args):
        # load config from file and command-line arguments
        cfg = get_cfg()
        add_deeplab_config(cfg)
        add_maskformer2_config(cfg)
        cfg.merge_from_file("assets/configs/maskformer2/maskformer2_R50_bs16_50ep.yaml")
        cfg.merge_from_list(["MODEL.WEIGHTS", "weights/mf2_model_final_94dc52.pkl"])
        cfg.freeze()
        return cfg

    def get_parser(self):
        parser = argparse.ArgumentParser(description="maskformer2 demo for builtin configs")
        parser.add_argument(
            "--confidence-threshold",
            type=float,
            default=0.5,
            help="Minimum score for instance predictions to be shown",
        )
        return parser    
    
    
if __name__ == "__main__":
    
    VDB = VideoDatabase("hsp-land")
    frame = VDB.get_frames_for_video("data/videos/DESPICABLEME_eng.mp4")[121]
    
    model = Mask2FormerWrapper()
    
    prediction, vis_output = model.process_image(frame)
    model.save_image(vis_output, "sample_mf2.png")
    model.save_matlab_output(prediction, "sample_mf2.mat")
    