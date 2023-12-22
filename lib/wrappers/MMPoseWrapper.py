
from mmpose.apis import MMPoseInferencer
from lib.utils.VideoDatabase import VideoDatabase
import cv2
from scipy.io import savemat
import pickle
import os 

class MMPoseWrapper:
    
    def __init__(self):

        self.name = "MMPose"

        self.inferencer = MMPoseInferencer('human')
        self.face_inferencer = MMPoseInferencer('face')
      
    def generate_poses_and_save(self, img_path):
        
        result_generator = self.inferencer(img_path, show=False, return_vis=True)
        result = next(result_generator)
        
        return result, cv2.cvtColor(result["visualization"][0],cv2.COLOR_BGR2RGB)
        
    def process_image(self, img_path):
        
        return self.generate_poses_and_save(img_path)

    def save_image(self, visualized_output, output_path):

        cv2.imwrite(output_path, visualized_output)        
    
    def generate_faces_and_save(self, img_path):
        
        result_generator = self.face_inferencer(img_path, show=False, return_vis=True)
        result = next(result_generator)
    
        return result
        
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
        
        
    def flatten(self, list_of_lists):
        return [item for row in list_of_lists for item in row]
    
    def save_matlab_output(self, predictions, output_path):
        
        keypoints = [entry['keypoints'] for entry in predictions['predictions'][0]]
        bboxes = [entry['bbox'] for entry in predictions['predictions'][0]]
        
        savemat(output_path, {'keypoints': keypoints, 'bboxes': bboxes})

    def save_pickle_output(self, predictions, output_path):
        
        keypoints = [entry['keypoints'] for entry in predictions['predictions'][0]]
        bboxes = [entry['bbox'] for entry in predictions['predictions'][0]]

        with open(output_path, 'wb') as fp:
            pickle.dump({'keypoints': keypoints, 'bboxes': bboxes}, fp)


if __name__ == "__main__":
    
    VDB = VideoDatabase("hsp-land")
    frame = VDB.get_frames_for_video("data/videos/DESPICABLEME_eng.mp4")[9]
    
    model = MMPoseWrapper()

    prediction, vis_output = model.process_image(frame)
    model.save_image(vis_output, "sample_mmpose.png")
    model.save_matlab_output(prediction, "sample_mmpose.mat")
