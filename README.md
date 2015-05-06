BrainMix
========

BrainMix is an application for image registration of brain slices and atlas annotations. 

Installation
------------
After cloning the repository, make sure the top `brainmix` folder is in your python path.
In Linux, just add the following line to your `.bashrc` :
```
export PYTHONPATH=$PYTHONPATH:BRAINMIXDIR
```
where `BRAINMIXDIR` is the path to the top `brainmix` folder.

Getting started
---------------
To run BrainMix and load images automatically, go to the folder containing `brainmixapp.py` (usually `brainmix/brainmix/`) and run:
```
python brainmixapp.py -i IMAGEFOLDER
```
This will load all images in `IMAGEFOLDER`.


