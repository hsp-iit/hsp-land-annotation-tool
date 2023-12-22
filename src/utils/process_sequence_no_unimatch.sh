#!/bin/bash

# showing help info in case the script is run incorrectly
if [ $# -lt 6 ]; then

    echo "[PROCESS VIDEO] Please provide a set of arguments: (1) the path to the sequence to process, (2) start time, (3) subsequence length, (4) promps for CLIP-Seg, (5) main output folder, (6) output folder for the multi-visualization, (7, optional) gaze data folder"
    exit 1

fi

video_title=$1
start_text="--start $2"
limit_text="--limit $3"
prompts=$4
output_folder=$5
output_folder_multivis=$6
gaze_text=""
output_folder_real=""

if [ $# -gt 6 ]; then
    output_folder_real="--output_real $7"
fi

if [ $# -gt 7 ]; then
    gaze_text="--gaze_data $8"
fi

python3 src/process_video.py --method mf2 --video $video_title --output $output_folder/mf2 $output_folder_real/mf2 $start_text $limit_text 

python3 src/process_video.py --method clipseg --video $video_title --output $output_folder/clipseg $output_folder_real/clipseg --prompts "$prompts" $start_text $limit_text 

python3 src/process_video.py --method spiga --video $video_title --output $output_folder/spiga $output_folder_real/spiga $start_text $limit_text

python3 src/process_video.py --method mmpose --video $video_title --output $output_folder/mmpose $output_folder_real/mmpose $start_text $limit_text

python3 src/process_video.py --method seem --video $video_title --output $output_folder/seem $output_folder_real/seem --prompts "$prompts" $start_text $limit_text

python3 src/viewers/multiview.py --format 1:base:images 1:spiga:$output_folder/spiga 1:mmpose:$output_folder/mmpose 2:clipseg:$output_folder/clipseg 2:mf2:$output_folder/mf2 3:seem:$output_folder/seem --output $output_folder_multivis --video $video_title --target_height 600 --padding 8 $start_text