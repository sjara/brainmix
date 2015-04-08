#!/usr/bin/env python
'''
registration_module_test.py
Written by: Kristi Potter
University of Oregon
Date: 1/20/15
Purpose: Program to test the registration of lab
images
Input: Directory containing jpg images, output directory
Output: Writes registered images to output directory
'''

import sys, os, glob
import numpy as np
sys.path.append("../Modules/")

# If we have itk installed, load those registration algs.
itkLoaded = True
try:
    import itk
    import itk_affine_registration   
except ImportError:
    itkLoaded = False
    print "ITK Methods not supported"

# If we have skimage installed, load those registration algs.
try:
    import skimage.io
except ImportError:
    sys.exit("please 'pip install scikit-image' to use this script")

# Function to test registration
def registration_module_test(inputDir):
    '''
    This function opens all images in a directory,
    converts them to the format for the module,
    passes in the images, and writes the returned
    images to the output directory.
    '''
    # Get all jpg files in directory
    imageFiles = glob.glob(os.path.join(inputDir, '*.jpg'))
    imageVolume = skimage.io.ImageCollection(imageFiles).concatenate()

    # If we have ITK, use that algorithm
    if itkLoaded:
        # ITK algorithms use ITK to read/write
        registered_images = itk_affine_registration.itk_affine_registration(imageFiles)

## -- Wrap main so we can call this via command line -- ##
if __name__ == '__main__':

    p1 = None
    
    if len(sys.argv) != 2:
        print "usage: registration_module_test inputDirectory"
        sys.exit()
    else:
        p1 = sys.argv[1]
   
    registration_module_test(p1)

