from lib.utils.VideoDatabase import VideoDatabase
import cv2
import pickle
from scipy.io import savemat
import os

import spiga.demo.analyze.track.get_tracker as tr
import spiga.demo.analyze.extract.spiga_processor as pr_spiga
from spiga.demo.analyze.analyzer import VideoAnalyzer
from spiga.demo.visualize.viewer import Viewer


class SPIGAWrapper:
    
    def __init__(self):

        self.name = "SPIGA"

        self.faces_tracker = None
        self.processor = None
        self.faces_analyzer = None
        self.viewer = None
    
    def initialize(self, img):
        
        self.faces_tracker = tr.get_tracker('RetinaSort')
        self.faces_tracker.detector.set_input_shape(img.shape[0], img.shape[1])

        self.processor = pr_spiga.SPIGAProcessor(dataset='wflw')

        # Initialize Analyzer
        self.faces_analyzer = VideoAnalyzer(self.faces_tracker, processor=self.processor)

        self.viewer = Viewer('None', width=img.shape[1], height=img.shape[0], fps=30)

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

      
    def process_image(self, img):
        
        if isinstance(img, str):
            img = cv2.imread(img)
        
        if self.faces_analyzer is None:
            self.initialize(img)
        
        tracked_obj = self.faces_analyzer.process_frame(img)
        self.viewer.process_image(img, drawers=[self.faces_analyzer], show_attributes=['face_id', 'landmarks', 'headpose'])
        
        return tracked_obj, self.viewer.canvas

    def save_image(self, img, filename):
        
        cv2.imwrite(filename, img)        
        
        
    def save_matlab_output(self, predictions, output_path):
        
        all_faces = list()
        
        for entry in predictions:
        
            cur_face = {'landmarks': entry.landmarks,
                        'key_landmarks': entry.key_landmarks,
                        'bbox': entry.bbox,
                        'face_id': entry.face_id}
                        
            all_faces.append(cur_face)
        
        savemat(output_path, {'faces': all_faces})

    def save_pickle_output(self, predictions, output_path):
        
        all_faces = list()
        
        for entry in predictions:
        
            cur_face = {'landmarks': entry.landmarks,
                        'key_landmarks': entry.key_landmarks,
                        'bbox': entry.bbox,
                        'face_id': entry.face_id}
                        
            all_faces.append(cur_face)
        
        with open(output_path, 'wb') as fp:
            pickle.dump({'faces': all_faces}, fp)

    
if __name__ == "__main__":
    
    VDB = VideoDatabase("hsp-land")
    frame = VDB.get_frames_for_video("data/videos/DESPICABLEME_eng.mp4")[121]
    
    model = SPIGAWrapper()
    
    predictions, visualization_output = model.process_image(frame)
    model.save_image(visualization_output, "spiga_sample.jpg")
    
    model.save_matlab_output(predictions, "spiga_sample.mat")