# **HSP-LAND**

This repository contains the source code needed to carry out a preliminary set of experiments within the HSP-LAND collaboration.

# :wrench: Installation & Requirements

The framework relies on the use of the code from a set of repositories available online.

All these codebases can be used in one of two ways, either:
- installing every repository locally on your machine, or 
- relying on the use of a Singularity container prepared ad-hoc.

## Repositories to install

To make use of all the functionalities available, the user should get and install the repositories listed below. 

Make sure that all the repositories are cloned and installed within the same root folder, e.g. `/home/user/source`.

- **Segmentation** 
  - Segment Anything [REPO](https://github.com/facebookresearch/segment-anything) - [PAPER](https://arxiv.org/abs/2304.02643)
  - CLIP-Seg [REPO](https://github.com/timojl/clipseg) - [PAPER](https://arxiv.org/abs/2112.10003)
  - Mask2Former [REPO](https://github.com/facebookresearch/Mask2Former) - [PAPER](https://arxiv.org/abs/2112.01527)
  - Segment Everything Everywhere All at Once [REPO](https://github.com/UX-Decoder/Segment-Everything-Everywhere-All-At-Once) - [PAPER](https://arxiv.org/abs/2304.06718)
- **Face Landmarks Estimation**
  - SPIGA [REPO](https://github.com/andresprados/spiga) - [PAPER](https://arxiv.org/abs/2210.07233)
- **Body Pose Estimation** 
  - MMPose [REPO](https://github.com/open-mmlab/mmpose)
- **Optical Flow Estimation** 
  - UniMatch [REPO](https://github.com/autonomousvision/unimatch) - [PAPER](https://arxiv.org/abs/2211.05783)
- **Tracking**
  - TAPIR [REPO](https://github.com/deepmind/tapnet) - [PAPER](https://arxiv.org/abs/2211.03726)

Once all the codebases have been set up, clone the `hsp-land-annotation-tool` repository within the same `/home/user/source` folder.

**NOTE**: in the following of this README, we assume that the user has stored all the codebases within the same `/home/user/source` directory.

Finally, download and install the [Anaconda package manager](https://www.anaconda.com/download). Once the installation is done, move to this repository folder and create the Anaconda environment from the .yml file available.

```bash
cd \home\usr\source
conda env create -f environment.yml
```

### Model Checkpoints

The user should create a `weights` folder within the `hsp-land-annotation-tool` repository. Here, they should gather the checkpoints needed by some of the techniques employed within this framework. At the time of writing of this README document (December 2023), the files contained in the `weights` folder are:

- gmflow-scale2-regrefine6-mixdata-train320x576-4e7b215d.pth (UniMatch)
- mf2_model_final_94dc52.pkl (Mask2Former)
- rd16-uni.pth (CLIPSeg)
- rd64-uni.pth (CLIPSeg)
- rd64-uni-refined.pth (CLIPSeg)
- seem_focall_v1.pt (Segment Everything Everywhere All At Once)

These files should be retrieved by the corresponding repositories, and copied within the `weights` directory just created.

At this point, everything should be set up correctly.

In case the user decides to follow the installation steps above, skip the following subsection (**Singularity Image**) and jump directly to **General**.

## Singularity Image (work in progress)

First, download the singularity image [available here]().

This section is a draft, and will be completed once the Singularity/Docker image will be available.

# General

This codebase has been built with a couple of objectives in mind:

- flexibility w.r.t. the set of videos employed 
- ease of use for external, non-technical users
- should be simple to expand with novel methods


## Flexibility w.r.t. the Set of Videos

This feature is enabled by the data structure used within the development of this repository, explained in the following.

### **Data Structure**

The data is organized in a way so that any video file can be included in the dataset, while mantaining a proper organization of the subfolders.

Irrespectively from the video original filename, each video is identified within the framework by a single incremental "ID", from 1 and onwards.

This codebase provides a transparent interface to include a novel video, or to retrieve an existing one, the `VideoDatabase` object, which is used mainly by the `src/utils/create_dataset.py` script.

This script handles the creation of a new dataset of videos, starting from the ones contained in a folder specified by the user. By opening a terminal and setting the working directory in the root folder of the repository, the script should be launched in the following way:

```bash
python src/utils/create_dataset.py --dataset hsp-land --folder data/videos
```

Assuming that the `data/videos` subfolder of the repository contains a set of video sequences, this will create the `data/databases/hsp-land.json` file, which acts as an auxiliary file to identify each video within the database:

```json
{
    "1": {
        "name": "data/videos/DESPICABLEME_eng.mp4",
        "fps": 24
    },
    "2": {
        "name": "data/videos/Fun_with_fractals.mp4",
        "fps": 30
    },
    "3": {
        "name": "data/videos/PRESENT.mp4",
        "fps": 24
    },
    "4": {
        "name": "data/videos/TOTORO_trees_eng.mp4",
        "fps": 30
    },
    "5": {
        "name": "data/videos/MICHELE.mp4",
        "fps": 30
    },
    "6": {
        "name": "data/videos/train_neutral.mp4",
        "fps": 30
    }
}
```

**NOTE**: the script above will also create all the frames corresponding to all the videos, stored within `data/<dataset_name>/<video_id>/images`.

After a few experiments or operations, the final data structure might look something like this:

```
data/ 
'-- databases/
'  '-- hsp-land.json
'-- hsp-land/
'   '-- 1/
'   '-- 2/
'   '-- 3/
'   '-- 4/
'   '-- 5/
'   '-- 6/
'       '-- images/
'           '-- frame-0000001.jpg
'           '-- frame-0000002.jpg
'           '-- ...
'       '-- results/
'           '-- unimatch/
'           '-- mf2/
'           '-- clipseg/
'               '-- frame-0000001.png
'               '-- frame-0000002.png
'               '-- ...
'-- videos/
    '-- DESPICABLEME_eng.mp4
    '-- Fun_with_fractals.mp4
    '-- PRESENT.mp4
    '-- TOTORO_trees_eng.mp4
    '-- MICHELE.mp4
    '-- train_neutral.mp4
```

For the sake of the following explanations, in the rest of this README, the folder `video_id/` (as in `1/`, `2/`, ..) for a given sequence will be called `<video_folder>`.


## Ease of Use

The framework is structured in a way to separate the pipeline in three macro-step:

- **dataset creation**: needed to convert a set of sequences from video files to frames, via the `src/utils/create_dataset.py` script
- **feature extraction**: driven by the scripts in the `src/sample` and `src/utils` directories
- **annotation and refinement**: carried out via the `lib/ui/interface.py` GUI-based program

### Dataset Creation

The creation of a dataset is handled by the `src/utils/create_dataset.py`, as described in the **Data Structure** section above.

### Feature Extraction

The repository is shipped with a sample script (`src/sample/sample_process.py`) which runs all the available algorithms on all the six initial videos considered for this project.

As it can be seen by inspecting its content, this file specifies the processing of a set of sequences, within specific intervals.

```python
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
```

**NOTE**: The `"limits"` entries should be specified in the format `(starting_time,duration_in_seconds)`.

To prepare and run the processing script, the user should now run the following commands in a terminal (note, this is a temporary solution):

```bash
conda activate hsp-land

export PYTHONPATH=:/home/user/source/clipseg:/home/user/source/Mask2Former:/home/user/source/Mask2Former/demo:/home/user/source/Segment-Everything-Everywhere-All-At-Once/demo_code:/home/user/source/unimatch:/home/user/source/tapnet
```

Finally, the user can start the actual processing step:

```bash
python src/utils/sample_process.py
```

The outcome of the processing will be saved in the `results/` and `results_files/` subfolders within the dataset directory tree, together with a multi-visualization involving the CLIP-Seg, SPIGA, MaskFormer2, MMPose, Segment Everything Everywhere All at Once, and UniMatch methods.

---

### More in detail: the `process_sequence.sh` script

This script carries out the processing with all the methods available and creates the "multi-visualization" from the results. 

For now, all the methods included in the framework are run sequentially, one further customization of this script will be in the direction of allowing to select the techniques to actually run once executed.

```bash
...

python3 src/smart_process_video.py --method clipseg ...

python3 src/smart_process_video.py --method spiga ...

python3 src/smart_process_video.py --method mf2 ...

python3 src/smart_process_video.py --method mmpose ...

python3 src/smart_process_video.py --method seem ...

python3 src/smart_process_video.py --method unimatch ...

python3 src/viewers/multiview.py --format 1:base:images 1:spiga:$output_folder/spiga 1:mmpose:$output_folder/mmpose 2:clipseg:$output_folder/clipseg 2:mf2:$output_folder/mf2 2:unimatch:$output_folder/unimatch 3:seem:$output_folder/seem --output $output_folder_multivis --video $video_title --target_height 600 --padding 8 $start_text
```

---

### Annotation Refinement

Once all the processing has been executed, the framework has completed the extraction of all the features required, for the videos within the dataset used.

The GUI provided within this framework exploits the information contained in the features extracted in the previous step, and allows the user to annotate the sequence in a fine-grained manner, creating custom entities (e.g. associated with the characters acting in the scenes) and the corresponding per-frame annotations.

![SPIGA](assets/images/gui.png)

The GUI can be launched with the following command:

```bash
python lib/ui/interface.py
```

After the interface has been loaded, the user should click on the "File..." menu, then on the "Open" entry. The user should then navigate to a subfolder within the `data/` directory corresponding to one of the videos which has been processed. Once there, they should click on the two folders which have been specified as the `output_folder_qualitative` and `output_folder_files` within the `sample_process.py` script.

Once the data is loaded, the user can proceed using the GUI to carry out the annotation, as explained in the video tutorial available [at this link]().
<!--
## Easy to Expand with Novel Methods

[explain the Wrapper idea and style]

 # Methods

[remove]

## CLIP-Seg

The user has the possibility to specify a set of `prompts`  to use and for which to decode the segmentation masks. In addition, there is the possibility to `limit` the processing to a reduced number of frames.

```bash
python3 src/process_video.py --video data/videos/DESPICABLEME_eng.mp4 --method clipseg --output results/clipseg --limit 50 --prompts "a man" "a girl" "a big curtain" "a monster with big teeth"
```

Once the computation is done, the default viewer can be used to produce a set of output images, one per each processed frame.

```bash
python3 src/viewers/view.py --method clipseg --folder results/clipseg --video data/videos/DESPICABLEME_eng.mp4 --output visualization/clipseg
```

![CLIP-Seg](assets/images/sample-clipseg.jpg)

## Segment Anything (SAM)

The default method implmented here makes use of the grid-based approach through which the Segment Anything dataset (SA-1B) has been created.

A set of points is sampled across the image, and used as the base for the prompt-based generation of the masks, as explained in Section 4 of the [Segment Anything paper](https://arxiv.org/abs/2304.02643).

**NOTE**: this is the output provided by using the default parameters for the algorithm. Further tuning would probably provide better masks.

```bash
python3 src/process_video.py --video data/videos/DESPICABLEME_eng.mp4 --method sam --output results/sam --limit 50
```

The outcome can be then visualized thanks to the `view.py` script.

```bash
python3 src/viewers/view.py --method sam --folder results/sam --video data/videos/DESPICABLEME_eng.mp4 --output visualizations/sam
```

![SAM](assets/images/sample-sam.jpg)

## SPIGA

This method relies on an external face detector (in this case, based on [RetinaFace](https://github.com/serengil/retinaface)) and provides an estimation of facial landmarks on top of the faces detected.

The calls to process a sequence using this method are similar to the previous ones, and are as follows:

```python
python3 src/process_video.py --video data/videos/DESPICABLEME_eng.mp4 --method spiga --output results/spiga --limit 50
```

```python
python3 src/viewers/view.py --method spiga --folder results/spiga --video data/videos/DESPICABLEME_eng.mp4 --output visualization/spiga
```

![SPIGA](assets/images/sample-spiga.jpg)


## MMPOSE

The algorithms implemented within the MMPose framework allow to estimate the pose for a set of different entities: human joints, animal joints, or face landmarks.

The default visualization implemented in the framework is the one related to human pose estimation, and the code can be used in the following way to produce qualitative output for that:

```python
python3 src/process_video.py --video data/videos/DESPICABLEME_eng.mp4 --method mmpose --output results/mmpose --limit 50
```

```python
python3 src/viewers/view.py --method mmpose --folder results/mmpose --video data/videos/DESPICABLEME_eng.mp4 --output visualization/mmpose
```

![SPIGA](assets/images/sample-mmpose.jpg)



## MaskFormer2

MaskFormer 2 is one of the top performing recent instance segmentation methods.

XXXXXXXXXXXXXX

```python
python3 src/process_video.py --video data/videos/DESPICABLEME_eng.mp4 --method mf2 --output results/mf2 --limit 50
```

```python
python3 src/viewers/view.py --method mf2 --folder results/mf2 --video data/videos/DESPICABLEME_eng.mp4 --output visualization/mf2
```

![SPIGA](assets/images/sample-mf2.jpg)
 -->
---

# Utilities

Included in this repositories are a set of utilities meant to ease the user experience when carrying out a set of specific tasks.

## Produce Dummy Gaze Data for Visualization 

Since the 

For now, for every image named `frame-XXXXXX.jpg`, the gaze visualization code expects a corresponding `frame-XXXXXX.txt` file to be available, containing the data about the gaze to be rendered.

The `frame-XXXXXX.txt` file contains entries (rows) in the format `x,y,label`, and the following examples shows the content of a sample gaze file:

```
0.7974334584121431,0.5391578576660154,3
0.5469894291992186,0.437883429175395,5
```

**NOTE**: the gaze is reported with values normalized within the 0-1 range, so that the visualization can work with any image format in the results

Since this gaze information might be unavailable, the `produce_gaze_data.py` script creates a set of files containing dummy gaze data entries for all the frames of a video.

```bash
python src/utils/produce_gaze_data.py --video data/videos/TOTORO_trees_eng.mp4
```

This will create and populate a `gaze/` folder within the dataset, for the video specified. At the moment, the folder is populated with entries representing two dummy gaze sequences with IDs `3` and `5`, moving respectively in a circular and an infinite-like pattern.

---

## A Note on the Multi-Visualization Script

The multi-visualization script is an utility (which is often invoked automatically during the processing) that allows to produce custom renderings of the results for an experiment.

In particular, it allows to compose mosaic-like visualizations, in order to appreciate qualitatively the outcome of the processing via the several methods available.

The following is an example of invocation of the multi-visualization script:

```bash
python3 src/viewers/multiview.py --format 1:base:images 1:spiga:results/spiga 2:clipseg:results/clipseg 3:mf2:results/mf2 3:mmpose:results/mmpose --output multivis --video "data/videos/DESPICABLEME_eng.mp4" --target_height 600 --padding 8 --gaze_data gaze 
```

In this specific call, the arguments are:

- `format`: a customized string that allows to 
- `output`: the subfolder of `<video_folder>` in which to store the result of the visualization
- `target_height`: the target height to use for every frame, in the final mosaic image
- `padding`: the white padding to insert between the frames
- `gaze_data`: the directory within the `<video_folder>` containing the gaze data for the sequence (as briefly explained in the section **Produce Dummy Gaze Data for Visualization**)

**NOTE**: the `format` parameter is the most crucial one to achieve the intended composed visualization of the multiple outputs computed. The string is formed by several `<row>:<visualization>:<folder>` entries each one specifying:

- in which `row` to draw the entry
- which `visualization` method to use (drives the way the output files are retrieved and rendered)
- from which `folder` to gather the results

In case several entries share the same `row` number, those are stacked horizontally one after another.

Thus, the string `--format 1:base:images 1:spiga:results/spiga 2:clipseg:results/clipseg 3:mf2:results/mf2 3:mmpose:results/mmpose` will drive the framework to produce output frames made composed in this way:

![MULTIVIS-EXPLAINED](assets/images/example-multivis-explained.png)

The argument `--gaze_data gaze` used in the call above also loads the "dummy" gaze data produced via another script available within this framework. The GIF below shows an example of the final results, displaying one frame at a time (remind that the output of the multi-visualization script is still represented by **single frames**).

<!-- ![MULTIVIS-EXPLAINED](assets/images/example-multivis-gaze.jpg) -->
![MULTIVIS-EXPLAINED](assets/images/example-multivis.gif)

---

## Recovering Results from an Experiment

The `src/utils/gather_results.py` provided allows to recover easily a set of folders resulting from a given experiment, by creating a single .zip file containing the material requested. 

This script makes use of the same convention introduced above, i.e. the results for a given video are retrieved by means of its filename. 

```bash
python3 src/utils/gather_results.py --video data/videos/DESPICABLEME_eng.mp4 --output results.zip --folders multivis
```

This call will zip the multi-visualization produced by running the code described previously in this repository, zipping all the frames into a `results.zip` file, which can then be easily retrieved remotely with any utility as the `scp` command.



<!-- 
At this point, it is possible to retrieve the frames for a specific video, with the possibility to subsample them (note that the number specified is not the target *framerate*, but instead just a subsampling factor):

```python
frames = VDB.get_frames_for_video("data/videos/Fun_with_fractals.mp4", subsample = 5)
```

At this point, we might need to create a novel folder for an experiment. Since the main idea is for the data structure to be transparent (at the code level), the user can obtain a new folder for a given video as in:

```python
output_folder = VDB.folder_for_video("results/sam", "data/videos/Fun_with_fractals.mp4")
```

This operation will create the folder tree `results/sam` within the data structure for the dataset, by exploiting the known `filename <-> ID` correspondences. -->
