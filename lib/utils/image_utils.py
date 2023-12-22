
import cv2
import os 
from Fancymages.lib.viz.drawing import Drawer
import numpy as np
from scipy.spatial.distance import cdist

# ------------------------------------------------
# General part

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

def equalize_height_images(images, target_height):
    
    images = [image_resize(im, height=target_height) if im.shape[0] != target_height else im for im in images]
    return images

def load_images_and_equalize_height(frame, exp_current_frames, target_height = None):
        
    frame_img = cv2.imread(frame)
    
    if target_height is None:
        target_height = frame_img.shape[0]
        
    images = [cv2.imread(f) for f in exp_current_frames]    
    images = [image_resize(im, height=target_height) if im.shape[0] != target_height else im for im in images]
  
    return frame_img, images

def pad_images_with_white(all_images, padding=10):
    
    for im_id in range(len(all_images)):
        
        all_images[im_id] = cv2.copyMakeBorder(
                                                all_images[im_id],
                                                top=0,
                                                bottom=0,
                                                left=padding,
                                                right=padding,
                                                borderType=cv2.BORDER_CONSTANT,
                                                value=[255, 255,255]
                                            )
        
    return all_images

def pad_images_with_white_vertical(all_images, padding=10):
    
    for im_id in range(len(all_images)):
        
        all_images[im_id] = cv2.copyMakeBorder(
                                                all_images[im_id],
                                                top=padding,
                                                bottom=padding,
                                                left=0,
                                                right=0,
                                                borderType=cv2.BORDER_CONSTANT,
                                                value=[255, 255,255]
                                            )
        
    return all_images

def enlarge_image(img, target_width):
    
    if img.shape[1] != target_width:
        img = cv2.copyMakeBorder(
                                    img,
                                    top=0,
                                    bottom=0,
                                    left=0,
                                    right=target_width-img.shape[1],
                                    borderType=cv2.BORDER_CONSTANT,
                                    value=[255, 255,255]
                                )

    return img

def overlay_gaze_data(img, gaze_folder, frame_name):
     
    drawer = Drawer(None)
    drawer.return_numpy = True
    drawer.default_style()

    gaze_filename = os.path.splitext(os.path.basename(frame_name))[0]
    gaze_filename = os.path.join(gaze_folder, f"{gaze_filename}.txt")
    
    with open(gaze_filename, "r") as gaze_file:
        data = gaze_file.readlines()
        
    for line in data:
        
        tokens = line.strip().split(",")
        
        x = int(float(tokens[0]) * img.shape[1])
        y = int(float(tokens[1]) * img.shape[0])
        metadata = tokens[2:]
        
        img = drawer.keypoints(img, [[x,y]], labels = [metadata[0]], font_size = 20)

    return img

def farthest_point_sampling(mask, num_points):
    
    points = np.array(list(zip(*np.nonzero(mask))))
    
    sampled_points = list()
    idx = np.random.randint(points.shape[0])
    sampled_points.append(points[idx])
    points = np.delete(points, idx, 0)

    for i in range(1, num_points):
        
        if points.shape[0] == 0:
            break

        distances = cdist(points, np.array(sampled_points))
        distances = np.min(distances, axis=1)
        farthest_index = np.argmax(distances)
        sampled_points.append(points[farthest_index])
        points = np.delete(points, farthest_index, 0)
        
    fps = np.array(sampled_points)    
        
    bw = np.zeros(mask.shape)

    for i in range(fps.shape[0]):       
        bw[int(fps[i,0]), int(fps[i,1])] = 255
    
    return bw, np.array(sampled_points)
    
# ---------------------------------------

def subsample_mask_numpoints(mask, num_points):
       
    mask_bool = mask != 0
    vals = np.random.rand(mask_bool.shape[0], mask_bool.shape[1])       
       
    cnz = np.count_nonzero(mask)
    target = 1.0 - num_points / cnz
    to_zero = np.logical_and(mask_bool,vals < target)
    mask[to_zero] = 0 
    
    return mask

# ---------------------------------------

def sample_points_mask_evenly(imgbw, width, height, num_points=30, k_size=11):

    kernel = np.ones((k_size, k_size), np.uint8)
    
    imgbw = cv2.erode(imgbw, kernel, iterations=1)
    imgbw = cv2.resize(imgbw, (width, height), interpolation = cv2.INTER_NEAREST)    
    
    imgbw, _ = farthest_point_sampling(imgbw, num_points)

    mask_indexes = np.nonzero(imgbw)
    points = [list(coords) for coords in zip(mask_indexes[0], mask_indexes[1])]
    
    y, x = zip(*points)
    
    x = np.array(list(x))[None].T
    y = np.array(list(y))[None].T
    t = np.random.randint(0, 1, (num_points, 1))

    points = np.concatenate((t, y, x), axis=-1).astype(np.int32)  

    return np.array(points)

# ---------------------------------------

def sample_points_mask(imgbw, width, height, num_points=20, k_size=11, mode="random"):

    kernel = np.ones((k_size, k_size), np.uint8)
    
    imgbw = cv2.erode(imgbw, kernel, iterations=1)
    imgbw = cv2.resize(imgbw, (width, height), interpolation = cv2.INTER_NEAREST)

    mask_indexes = np.nonzero(imgbw)
    
    points = [list(coords) for coords in zip(mask_indexes[0], mask_indexes[1])]
    
    if mode == "random":
        points = random.sample(points, num_points)
    else:
        points = None
    
    y, x = zip(*points)
    t = np.random.randint(0, 1, (num_points, 1))

    x = np.array(list(x))[None].T
    y = np.array(list(y))[None].T
    
    points = np.concatenate((t, y, x), axis=-1).astype(np.int32)  

    return points

