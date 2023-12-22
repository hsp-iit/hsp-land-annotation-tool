
import haiku as hk
import jax
import mediapy as media
import numpy as np
import tree
import cv2
import os 

from tapnet import tapir_model
from tapnet.utils import transforms
from tapnet.utils import viz_utils

from lib.utils.image_utils import sample_points_mask
from assets.configs.tapir.config import tapir_checkpoint

class TAPIRWrapper:
    
    def __init__(self, num_points=30):
        
        self.name = "tapir"
        
        self.resize_height = 256  
        self.resize_width = 256  
        self.num_points = num_points  
        
        ckpt_state = np.load(tapir_checkpoint, allow_pickle=True).item()
        self.params, self.state = ckpt_state['params'], ckpt_state['state']
        
        model = hk.transform_with_state(self.build_model)
        self.model_apply = jax.jit(model.apply)
        

    def build_model(self, frames, query_points):

        """Compute point tracks and occlusions given frames and query points."""
        model = tapir_model.TAPIR(bilinear_interp_with_depthwise_conv=False, pyramid_level=0)
        outputs = model(
            video=frames,
            is_training=False,
            query_points=query_points,
            query_chunk_size=64,
        )
        return outputs

    def preprocess_frames(self, frames):
        """Preprocess frames to model inputs.

        Args:
            frames: [num_frames, height, width, 3], [0, 255], np.uint8

        Returns:
            frames: [num_frames, height, width, 3], [-1, 1], np.float32
        """
        frames = frames.astype(np.float32)
        frames = frames / 255 * 2 - 1
        return frames

    def postprocess_occlusions(self, occlusions, expected_dist):
        """Postprocess occlusions to boolean visible flag.

        Args:
            occlusions: [num_points, num_frames], [-inf, inf], np.float32
            expected_dist: [num_points, num_frames], [-inf, inf], np.float32

        Returns:
            visibles: [num_points, num_frames], bool
        """
        visibles = (1 - jax.nn.sigmoid(occlusions)) * (1 - jax.nn.sigmoid(expected_dist)) > 0.5
        return visibles

    def inference(self, frames, query_points):
        """Inference on one video.

        Args:
            frames: [num_frames, height, width, 3], [0, 255], np.uint8
            query_points: [num_points, 3], [0, num_frames/height/width], [t, y, x]

        Returns:
            tracks: [num_points, 3], [-1, 1], [t, y, x]
            visibles: [num_points, num_frames], bool
        """
        # Preprocess video to match model inputs format
        frames = self.preprocess_frames(frames)
        # num_frames, height, width = frames.shape[0:3]
        query_points = query_points.astype(np.float32)
        frames, query_points = frames[None], query_points[None]  # Add batch dimension

        # Model inference
        rng = jax.random.PRNGKey(42)
        outputs, _ = self.model_apply(self.params, self.state, rng, frames, query_points)
        outputs = tree.map_structure(lambda x: np.array(x[0]), outputs)
        tracks, occlusions, expected_dist = outputs['tracks'], outputs['occlusion'], outputs['expected_dist']

        # Binarize occlusions
        visibles = self.postprocess_occlusions(occlusions, expected_dist)
        return tracks, visibles

    def convert_grid_coordinates(self, tracks, resize_sz, sz):
        
        return transforms.convert_grid_coordinates(tracks, resize_sz, sz)


if __name__ == "__main__":
        
    tapir = TAPIRWrapper()
    
    base_dir = "/home/iit.local/dmalafronte/Private/HSP_LAND/Source/hsp_land/data/hsp-land/1/images"
    all_frames = os.listdir(base_dir)
    all_frames.sort()
    # video = [cv2.cvtColor(cv2.imread(os.path.join(base_dir, img)), cv2.COLOR_BGR2RGB) for img in all_frames[24:84]]
    video = [cv2.cvtColor(cv2.imread(os.path.join(base_dir, img)), cv2.COLOR_BGR2RGB) for img in all_frames[24:34]]
    video = np.stack(video, axis=0)
    frames = media.resize_video(video, (tapir.resize_height, tapir.resize_width))
    height, width = video.shape[1:3]
    
    mask_path = "/home/iit.local/dmalafronte/Private/HSP_LAND/Source/hsp_land/data/aux/DESPICABLEME_frame-000025-base-mask.jpg"
    mask_img = cv2.imread(mask_path)
    query_points = sample_points_mask(mask_img, tapir.resize_width, tapir.resize_height, tapir.num_points)

    print("-- Inference.")

    tracks, visibles = tapir.inference(frames, query_points)

    print("-- Visualization.")

    # Visualize sparse point tracks
    tracks = transforms.convert_grid_coordinates(tracks, (tapir.resize_width, tapir.resize_height), (width, height))
    video_viz = viz_utils.paint_point_track(video, tracks, visibles)

    output_video = "/home/iit.local/dmalafronte/Private/HSP_LAND/Source/hsp_land/data/hsp-land/1/tapir_wrapper.mp4"
    media.write_video(output_video, video_viz, fps=24, qp=18)

