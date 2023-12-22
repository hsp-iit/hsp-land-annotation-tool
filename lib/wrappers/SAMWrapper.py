
import numpy as np
import matplotlib.pyplot as plt
import cv2

import sys
sys.path.append("..")
from segment_anything import sam_model_registry, SamPredictor
from lib.utils.VideoDatabase import VideoDatabase

class SAMWrapper:

    def __init__(self):

        self.name = "SAM"

        sam_checkpoint = "/home/iit.local/dmalafronte/Downloads/sam_vit_b_01ec64.pth"
        model_type = "vit_b"
        device = "cuda"
        device = "cpu"

        self.model = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        self.model.to(device=device)
        
        self.predictor = SamPredictor(self.model)

    def show_mask(self, mask, ax, random_color=False):
        if random_color:
            color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
        else:
            color = np.array([30/255, 144/255, 255/255, 0.6])
        h, w = mask.shape[-2:]
        mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
        ax.imshow(mask_image)

    def show_points(self, coords, labels, ax, marker_size=375):
        pos_points = coords[labels==1]
        neg_points = coords[labels==0]
        ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
        ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white', linewidth=1.25)

    def show_box(self, box, ax):
        x0, y0 = box[0], box[1]
        w, h = box[2] - box[0], box[3] - box[1]
        ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0,0,0,0), lw=2))

    def draw_anns(self, anns):

        if len(anns) == 0:
            return

        sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)

        ax = plt.gca()
        ax.set_autoscale_on(False)

        img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
        img[:,:,3] = 0
        for ann in sorted_anns:
            m = ann['segmentation']
            color_mask = np.concatenate([np.random.random(3), [0.35]])
            img[m] = color_mask
        ax.imshow(img)

        plt.axis('off')

        return img

    def generate_save_masks(self, image_filename, filename):

        image = cv2.imread(image_filename)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        plt.figure(figsize=(20,20))
        plt.imshow(image)

        masks = self.mask_generator_tuned.generate(image)
        img = self.draw_anns(masks)

        plt.savefig(filename, bbox_inches='tight', pad_inches=0.0)
        plt.close()

        return img

    def save_masks_img(self, filename, img):

        cv2.imwrite(filename, img)

    def generate_from_points(self, image, input_points):

        self.predictor.set_image(image)

        input_label = np.ones((input_points.shape[0],))

        masks, _, _ = self.predictor.predict(
                            point_coords=input_points,
                            point_labels=input_label,
                            mask_input=None,
                            multimask_output=False,
                            )

        masks = np.squeeze(masks)
        bw = np.zeros(masks.shape)
        bw[masks] = 255

        return bw


if __name__ == "__main__":

    VDB = VideoDatabase("hsp-land")

    frame = VDB.get_frames_for_video("data/videos/DESPICABLEME_eng.mp4")[5:10]

    sam = SAMWrapper()
    masks = sam.generate_save_masks(frame, "sam_sample.jpg")
