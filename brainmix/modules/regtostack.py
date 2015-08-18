'''
This module currently only has a function for our registration of 2.5 mag images to 1.25 images. It can be expanded
for other cases of registering one stack of images to another.
'''

import numpy as np
from brainmix.modules import imregistration as imreg
import scipy.misc

def downscale_stack_register(regstack, sourcestack, downscale, corner=(0,0)):
    '''
    Registers each image in a stack to the corresponding image in another stack.
    
    This method is for aligning images taken at different magnifications. The inputs are an aligned stack of the lower
    magnification images, a stack of the higher magnification images, the scale factor that will be applied to the 
    higher magnification images to make the areas of interest the same size in both magnifications (only for the 
    purpouses of registration), and a pair of coordinates marking the area of the lower magnification image that will
    be registered to. 
    
    Args:
        regstack (list of images): stack of registered images that will be the template for registration
        sourcestack (list of images): stack of images that will be aligned to regstack
        downscale (float): scaling factor by which each image in sourcestack will be downscaled
        corner (tuple): the top left corner of the area in each image of regstack that sourcestack will be aligned to
        
    Returns:
        regdownstack (list of image): registered sourcestack
    '''
    regstackquarter = []
    height, width = regstack[0].shape
    normcorner = (float(corner[0])/width, float(corner[1])/height)
    for image in range(len(regstack)):
        #The section of the 1.25 image that's being registered to still has to be manually selected
        img = image_crop(regstack[image], (normcorner[0],normcorner[0]+downscale), (normcorner[1],normcorner[1]+downscale))
        regstackquarter.append(img)
    downstack = []
    for image in range(len(sourcestack)):
        img = scipy.misc.imresize(sourcestack[image], downscale, interp='cubic')
        downstack.append(img)
    regdownstack = []
    pyramidDepth = imreg.get_pyramid_depth(downstack[image])
    for image in range(len(downstack)):
        tfrm = imreg.rigid_body_registration(downstack[image], regstackquarter[image], pyramidDepth, 2)
        tfrm[1:] /= downscale
        img = imreg.rigid_body_transform(sourcestack[image], tfrm)
        regdownstack.append(img)
    return regdownstack
        
def image_crop(image, normxcrop, normycrop):
    height, width = image.shape
    xcrop = np.array(normxcrop)*width
    ycrop = np.array(normycrop)*height
    outimg = image[ycrop[0]:ycrop[1], xcrop[0]:xcrop[1]]
    return outimg