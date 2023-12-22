
import mediapy as media
import numpy as np
import cv2

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QProgressBar

from lib.wrappers.TAPIRWrapper import TAPIRWrapper
from lib.wrappers.SAMWrapper import SAMWrapper
from lib.utils.generic_utils import draw_points

from lib.utils.image_utils import sample_points_mask_evenly


import matplotlib as mpl
import os
import pickle

from collections import Counter

class Refinement(object):

    def __init__(self, pickle_folder):
        
        self.sam = SAMWrapper()
        self.window_name = "Refinement Result"
        self.pickle_folder = pickle_folder
        
    def set_frames(self, frames):
        
        self.tapir = TAPIRWrapper(num_points=25)
        
        self.all_images = frames
        self.video_frames = [cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB) for f in self.all_images]
        self.video = np.stack(self.video_frames, axis=0)
        self.frames = media.resize_video(self.video, (self.tapir.resize_height, self.tapir.resize_width))
        self.height, self.width = self.video.shape[1:3]
        
    def set_starting_mask(self, mask):
        
        self.mask = mask
  
    def get_pickle_files_seem(self, secondary):
      
        self.all_pickle_files = [f.replace("images", f"{os.path.basename(self.pickle_folder)}/seem").replace(".jpg",f"-{secondary}.pkl") for f in self.all_images]
        self.all_pickles = list()
        
        for f in self.all_pickle_files:
            with open(f, 'rb') as fp:
                data = pickle.load(fp)
                self.all_pickles.append(data)
        
  
    def get_pickle_files_mf2(self, secondary=None):
      
        self.all_pickle_files = [f.replace("images", f"{os.path.basename(self.pickle_folder)}/mf2").replace(".jpg",".pkl") for f in self.all_images]
        self.all_pickles = list()
        
        for f in self.all_pickle_files:
            with open(f, 'rb') as fp:
                data = pickle.load(fp)
                data["classes"] = ["None"] + data["classes"]
                self.all_pickles.append(data)
        
    def get_pickle_files(self, method, secondary):
      
        func = getattr(self, f'get_pickle_files_{method}')
        func(secondary)

              
    def refine_seem(self, mode="voting"):
              
        print("-- Inference.")
        self.query_points = sample_points_mask_evenly(self.mask, self.tapir.resize_width, self.tapir.resize_height, num_points=self.tapir.num_points)
        
        tracks, _ = self.tapir.inference(self.frames, self.query_points)
                
        print("-- Done.")

        # Visualize sparse point tracks
        
        sz = self.all_pickles[0]["mask"].shape
        conv_tracks = self.tapir.convert_grid_coordinates(tracks, (self.tapir.resize_width, self.tapir.resize_height), (sz[1], sz[0]))
        tracks = self.tapir.convert_grid_coordinates(tracks, (self.tapir.resize_width, self.tapir.resize_height), (self.width, self.height))
        
        if mode == "centroid":
            average_points = np.mean(conv_tracks, axis=0)
        else:
            average_points = None

        all_masks = list()

        correct = list()
        
        for i, f in enumerate(self.all_pickles):
          
            if average_points is None:
              
                indexes = [f["mask"][int(conv_tracks[t_ind][i][1]), int(conv_tracks[t_ind][i][0])] for t_ind in range(conv_tracks.shape[0])]              
                counter = Counter(indexes)
                index = counter.most_common(1)[0][0]

            else:

                index = f["mask"][int(average_points[i][1]), int(average_points[i][0])]
                
            correct.append(index == 1)

            mask = f["mask"] == 1
                            
            bw = np.zeros(mask.shape)
            bw[mask] = 255
                    
            all_masks.append(bw)

        color_map = mpl.cm.get_cmap('tab20')
        
        all_results = list()
        
        zeroes_mat = np.zeros(all_masks[0].shape)
        zeroes_mat = np.expand_dims(zeroes_mat,axis=2)            
            
        for i, m in enumerate(all_masks):
                    
            if not correct[i]:
                bw = self.sam.generate_from_points(self.video_frames[i], np.squeeze(tracks[:,i,:]))
                bw = cv2.resize(bw, (all_masks[0].shape[1], all_masks[0].shape[0]), interpolation = cv2.INTER_AREA)
                bw = np.expand_dims(bw,axis=2)                
                rgb = np.concatenate((bw,zeroes_mat,zeroes_mat),axis=2)            

            else:
                bw = np.expand_dims(m,axis=2)       
                rgb = np.concatenate((zeroes_mat,bw,zeroes_mat),axis=2)            
            
            rgb = draw_points(rgb, np.squeeze(conv_tracks[:,i,:]), color_map)

            all_results.append((rgb, bw))
          
        annotation = list()  
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        for frame_id, (rgb, bw) in enumerate(all_results):

          cv2.imshow(self.window_name, rgb)            
          cv2.waitKey(0)
          
          annotation.append((self.all_images[frame_id], (rgb, bw)))
          
        cv2.destroyWindow(self.window_name)
          
          
        return annotation

              
    def refine_mf2(self, mode="voting"):
                
        print("-- Inference.")
        self.query_points = sample_points_mask_evenly(self.mask, self.tapir.resize_width, self.tapir.resize_height, num_points=self.tapir.num_points)
                
        tracks, _ = self.tapir.inference(self.frames, self.query_points)
                
        print("-- Done.")

        # Visualize sparse point tracks
        tracks = self.tapir.convert_grid_coordinates(tracks, (self.tapir.resize_width, self.tapir.resize_height), (self.width, self.height))
                
        if mode == "centroid":
            average_points = np.mean(tracks, axis=0)
        else:
            average_points = None

        all_masks = list()

        first_class = None
        correct = list()
        
        for i, f in enumerate(self.all_pickles):
          
          
            if average_points is None:
              
                indexes = [f["masks"][int(tracks[t_ind][i][1]), int(tracks[t_ind][i][0])] for t_ind in range(tracks.shape[0])]              
                counter = Counter(indexes)
                index = counter.most_common(1)[0][0]

            else:

                index = f["masks"][int(average_points[i][1]), int(average_points[i][0])]
                
            mask = f["masks"] == index
                
            if first_class is None:
              first_class = self.all_pickles[i]["classes"][index]
            elif first_class != self.all_pickles[i]["classes"][index]:
              print(f"[REFINE] Found class {self.all_pickles[i]['classes'][index]} when expecting {first_class}")  
            
            correct.append(first_class == self.all_pickles[i]["classes"][index])
            
            bw = np.zeros(mask.shape)
            bw[mask] = 255
                    
            all_masks.append(bw)
            
        color_map = mpl.cm.get_cmap('tab20')
        
        all_results = list()
        
        zeroes_mat = np.zeros(all_masks[0].shape)
        zeroes_mat = np.expand_dims(zeroes_mat,axis=2)            
            
        msgBox = QMessageBox( QMessageBox.Warning, "Processing..", "Processing with SAM.", QMessageBox.NoButton )
        # Get the layout
        l = msgBox.layout()
        # Hide the default button
        l.itemAtPosition( l.rowCount() - 1, 0 ).widget().hide()
        progress = QProgressBar()
        progress.reset()
        # Add the progress bar at the bottom (last row + 1) and first column with column span
        l.addWidget(progress,l.rowCount(), 0, 1, l.columnCount(), Qt.AlignCenter )
        msgBox.setModal(False)            
        msgBox.show()            
            
        for i, m in enumerate(all_masks):
            
            progress.setValue(int(i/len(all_masks)))
            msgBox.update()
            
            if not correct[i]:
                bw = self.sam.generate_from_points(self.video_frames[i], np.squeeze(tracks[:,i,:]))
                bw = np.expand_dims(bw,axis=2)            
                rgb = np.concatenate((bw,zeroes_mat,zeroes_mat),axis=2)                        
            else:
                bw = np.expand_dims(m,axis=2)            
                rgb = np.concatenate((zeroes_mat,bw,zeroes_mat),axis=2)            

            rgb = draw_points(rgb, np.squeeze(tracks[:,i,:]), color_map)
            all_results.append((rgb,bw))

        msgBox.hide()

        annotation = list()  

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        for frame_id, (rgb,bw) in enumerate(all_results):

          cv2.imshow(self.window_name, rgb)
          cv2.waitKey(0)

          annotation.append((self.all_images[frame_id], (rgb,bw)))
          
        cv2.destroyWindow(self.window_name)
          
        return annotation
              
    def refine(self, method):
                
        func = getattr(self, f'refine_{method}')
        return func()
