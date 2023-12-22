import os

# target folder where to store the qualitative outputs
output_folder_qualitative = "results"
output_folder_multi_visualization = "multivis"
output_folder_files = "results_files"

# list of (sub)sequences to process
sequences = [
             {"name": "data/videos/DESPICABLEME_eng.mp4",
              "prompts": "'girl with a blue pajama' 'girl with a green sweater' 'girl with glasses' 'man' 'little girl'",
              "limits": ("1:46","3s"),
              "gaze": ""},
             
             {"name": "data/videos/Fun_with_fractals.mp4",
              "prompts": "'broccoli'",
              "limits": ("1:09","3s"),
              "gaze": ""},
             
             {"name": "data/videos/PRESENT.mp4",
              "prompts": "'a boy' 'a dog' 'a door'",
              "limits": ("3:03","3s"),
              "gaze": ""},
             
             {"name": "data/videos/TOTORO_trees_eng.mp4",
              "prompts": "'a child' 'a bunny like monster' 'a tree'",
              "limits": ("2:15","3s"),
              "gaze": ""},

             {"name": "data/videos/MICHELE.mp4",
              "prompts": "'a man' 'a chair' 'a tv screen'",
              "limits": ("0:48","3s"),
              "gaze": ""},

             {"name": "data/videos/train_neutral.mp4",
              "prompts": "'a child' 'a woman' 'a toy car'",
              "limits": ("0:03","3s"),
              "gaze": ""}

             ]

# main processing loop
for seq in sequences:

    cmd = f"./src/utils/process_sequence.sh {seq['name']} {seq['limits'][0]} {seq['limits'][1]} \"{seq['prompts']}\" {output_folder_qualitative} {output_folder_multi_visualization} {output_folder_files} {seq['gaze']}"
    
    print(f"[EXP DEBUG PICKLE] Running: {cmd}")
    os.system(cmd)