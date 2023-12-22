
import re
import cv2

def adjust_frames(frames, info, args):
      
    if args.start is not None:
        start_frame = convert_notation_to_frames(args.start, info["fps"])
        frames = frames[start_frame:]
    elif args.start_frame is not None:
        frames = frames[start_frame:]
                    
    if args.limit is not None:
        limit_frame = convert_notation_to_frames(args.limit, info["fps"])
        frames = frames[:limit_frame]
    elif args.limit_frame is not None:
        frames = frames[:limit_frame]
            
    return frames

def convert_notation_to_frames(text, video_fps):
    
    elems = re.search("(.*)m(.*)s", text, re.IGNORECASE)
    
    if elems:
        min = int(elems.groups()[0])
        sec = int(elems.groups()[1])
        return video_fps * (60*min + sec)

    elems = re.search("(.*)m", text, re.IGNORECASE)
    
    if elems:
        min = int(elems.groups()[0])
        return video_fps * 60*min

    elems = re.search("(.*)s", text, re.IGNORECASE)
    
    if elems:
        sec = int(elems.groups()[0])
        return video_fps * sec

    elems = re.search("(.*):(.*)", text, re.IGNORECASE)
    
    if elems:
        min = int(elems.groups()[0])
        sec = int(elems.groups()[1])
        return video_fps * (60*min + sec)

    return None


def draw_points(image, points, colors):
        
    for i in range(points.shape[0]):
        
        p = (int(points[i,0]), int(points[i,1]))
        image = cv2.circle(image, p, 5, colors(i), -1)
        
    return image
    

if __name__ == "__main__":
    
    notations = ["1m50s",
                 "50s",
                 "1m50s",
                 "1M50s",
                 "1:50"]
    
    sample_fps = 30
    
    for timing in notations:

        frames = convert_notation_to_frames(timing, sample_fps)
        print(f"Notation {timing} converted to {frames} (at {sample_fps} fps)")