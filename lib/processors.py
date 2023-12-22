
import os

SAVE_AS_MATLAB = False

# ------------------------------------------------

def process_sam(model, frames, output_folder, output_folder_real, args):
    
    print(f"[PROCESS] Processing with {model.name}-Anything...")
        
    for frame in frames:
        
        frame_name = os.path.basename(frame)
        output_name = os.path.join(output_folder, frame_name)
        
        model.generate_save_masks(frame, output_name)
    
    print(f"[PROCESS] Processed a total of {args.limit} frames.")
    print()

# ------------------------------------------------

def process_clipseg(model, frames, output_folder, output_folder_real, args):
    
    print(f"[PROCESS] Processing with {model.name}...")
        
    for frame in frames:
        
        frame_name, ext = os.path.splitext(os.path.basename(frame))
        
        predictions, masks = model.process_image_text(frame, args.prompts)
        
        for index, (prompt, mask) in enumerate(zip(args.prompts, masks)):
            
            output_name = os.path.join(output_folder, f"{frame_name}-{prompt}{ext}")
            model.save_image(mask, output_name)    
            
            if output_folder_real is not None:
                
                if SAVE_AS_MATLAB:
                
                    output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}-{prompt}.mat")
                    model.save_matlab_output(predictions[index], output_name_mat)

                else:
                
                    output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}-{prompt}.pkl")
                    model.save_pickle_output(predictions[index], output_name_pkl)

            
    
    print(f"[PROCESS] Processed a total of {args.limit} frames.")
    print()

# ------------------------------------------------

def process_spiga(model, frames, output_folder, output_folder_real, args):
    
    print(f"[PROCESS] Processing with {model.name}...")
        
    for frame in frames:
        
        frame_name = os.path.basename(frame)
        output_name = os.path.join(output_folder, frame_name)

        prediction, vis_output = model.process_image(frame)
        model.save_image(vis_output, output_name)        
        
        if output_folder_real is not None:
            
            if SAVE_AS_MATLAB:
            
                output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.mat")
                model.save_matlab_output(prediction, output_name_mat)

            else:
            
                output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.pkl")
                model.save_pickle_output(prediction, output_name_pkl)
            

    print(f"[PROCESS] Processed a total of {args.limit} frames.")
    print()

# ------------------------------------------------

def process_mf2(model, frames, output_folder, output_folder_real, args):
    
    print(f"[PROCESS] Processing with {model.name}...")
        
    for frame in frames:
        
        frame_name = os.path.basename(frame)
        output_name = os.path.join(output_folder, frame_name)
                
        prediction, vis_output = model.process_image(frame)
        model.save_image(vis_output, output_name)
        
        if output_folder_real is not None:
            
            if SAVE_AS_MATLAB:

                output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.mat")
                model.save_matlab_output(prediction, output_name_mat)
        
            else:        

                output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.pkl")
                model.save_pickle_output(prediction, output_name_pkl)
    
    print(f"[PROCESS] Processed a total of {args.limit} frames.")
    print()
    
# ------------------------------------------------

def process_mmpose(model, frames, output_folder, output_folder_real, args):
    
    print(f"[PROCESS] Processing with {model.name}...")
        
    for frame in frames:
        
        frame_name = os.path.basename(frame)
        output_name = os.path.join(output_folder, frame_name)
                
        prediction, vis_output = model.process_image(frame)
        model.save_image(vis_output, output_name)
        
        if output_folder_real is not None:

            if SAVE_AS_MATLAB:
            
                output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.mat")
                model.save_matlab_output(prediction, output_name_mat)            
            
            else:
                
                output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.pkl")
                model.save_pickle_output(prediction, output_name_pkl)            
    
    print(f"[PROCESS] Processed a total of {args.limit} frames.")
    print()

# ------------------------------------------------

def process_seem(model, frames, output_folder, output_folder_real, args):
    
    print(f"[PROCESS] Processing with {model.name}...")
        
    for frame in frames:
        
        frame_name, ext = os.path.splitext(os.path.basename(frame))
        
        predictions, masks = model.process_image(frame, args.prompts)
        
        for index, (prompt, mask) in enumerate(zip(args.prompts, masks)):
            
            output_name = os.path.join(output_folder, f"{frame_name}-{prompt}{ext}")
            model.save_image(mask, output_name)    
    
            if output_folder_real is not None:
                
                if SAVE_AS_MATLAB:
                        
                        output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}-{prompt}.mat")                
                        model.save_matlab_output(predictions[index], output_name_mat)
        
                else:
    
                        output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}-{prompt}.pkl")                
                        model.save_pickle_output(predictions[index], output_name_pkl)

    
    print(f"[PROCESS] Processed a total of {args.limit} frames.")
    print()
    
# ------------------------------------------------    

def process_unimatch(model, frames, output_folder, output_folder_real, args):
    
    print(f"[PROCESS] Processing with {model.name}...")
        
    for frame1, frame2 in zip(frames[:-1], frames[1:]):
        
        frame_name, ext = os.path.splitext(os.path.basename(frame1))
        
        prediction, flow_img = model.process_images(frame1, frame2, args)
        output_name = os.path.join(output_folder, f"{frame_name}{ext}")
        
        model.save_image(flow_img, output_name)
            
        if output_folder_real is not None:
            
            
            if SAVE_AS_MATLAB:
            
                output_name_mat = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.mat")
                model.save_matlab_output(prediction, output_name_mat)
        
            else:
                
                output_name_pkl = os.path.join(output_folder_real, f"{os.path.splitext(frame_name)[0]}.pkl")
                model.save_pickle_output(prediction, output_name_pkl)
                        

    print(f"[PROCESS] Processed a total of {args.limit} frames.")
    print()

