import imregistration as imreg
import numpy as np
import matplotlib.pyplot as plt
import skimage.io
from scipy import interpolate

def stack_register(stack, target=0):
    '''
    Register a stack of images to each other. A target image is specified that all others will be 
    registered to (the first image if none is specified). The target's neighbors will be registered to
    the target, and then every subsequent image will be registered to its neighbor, resulting in a stack
    of registered images in the same orientation as the target.

    Args: 
        stack (list of np.ndarray): stack of images for registration
        target (int): optional: index of image that will be registered to. Defaults to 0 (first image)

    Returns:
        outstack (np.ndarray): stack of registered images
    '''
    outimg = stack[target]
    outstack2 = [outimg]
    outstack = []
    pyramidDepth = get_pyramid_depth(stack[target])
    minLevel = 3
    if target != len(stack):
        for image in range(target+1, len(stack)):
            print image
            tfrm = imreg.rigid_body_registration(stack[image], outimg, pyramidDepth, minLevel)
            outimg = rigid_body_transform(stack[image], tfrm)
            outstack2.append(outimg)
    outimg = stack[target]
    if target != 0:
        for image in reversed(range(target)):
            print image
            tfrm = imreg.rigid_body_registration(stack[image], outimg, pyramidDepth, minLevel)
            outimg = rigid_body_transform(stack[image], tfrm)
            outstack.append(outimg)
        outstack = outstack[::-1]
        outstack.extend(outstack2)
    return outstack
        
def get_pyramid_depth(image):
    '''
    Computes the depth of the pyramids that will be created and used during image registration.

    Args: 
        image (np.ndarray): original image

    Returns:
        pyramidDepth (int): number of layers in pyramids
    '''
    pyramidDepth = 1
    width = image.shape[1]
    height = image.shape[0]
    while width > 24 or height > 24:
        width /= 2
        height /= 2
        pyramidDepth += 1
    return pyramidDepth

def rigid_body_transform(image, tfrm):
    '''
    Apply a rigid-body transformation to an image (grayscale).

    Args: 
        image (np.ndarray): original image
        tfrm (np.ndarray): (3,) transformation [rotation_angle, translation_x, translation_y]

    Returns:
        outimg (np.ndarray): A transformed image.
    '''
    '''
    width = image.shape[1]
    height = image.shape[0]
    grid = np.meshgrid(np.arange(width), np.arange(height))
    coords = np.vstack(grid).reshape(2, width*height)
    spline = interpolate.RectBivariateSpline(np.arange(height), np.arange(width), image)
    outimg = rbr.rigidBodyTransform(spline, width, height, coords, tfrm)
    '''
    skTransform = skimage.transform.SimilarityTransform(rotation=tfrm[0], translation=tfrm[1:])
    outimg = skimage.transform.warp(image,skTransform)
    return outimg


if __name__=='__main__':
    import os
    datadir = '/data/brainmix_data/test043_TL'
    print 'Loading data...'
    img1 = skimage.io.imread(os.path.join(datadir,'p1-F1-01b.jpg'),as_grey=True)
    img2 = skimage.io.imread(os.path.join(datadir,'p1-F2-01b.jpg'),as_grey=True)
    img3 = skimage.io.imread(os.path.join(datadir,'p1-F3-01b.jpg'),as_grey=True)
    img4 = skimage.io.imread(os.path.join(datadir,'p1-F4-01b.jpg'),as_grey=True)
    img5 = skimage.io.imread(os.path.join(datadir,'p1-F5-01b.jpg'),as_grey=True)
    img6 = skimage.io.imread(os.path.join(datadir,'p1-F6-01b.jpg'),as_grey=True)
    stack = [img1, img2, img3, img4, img5, img6]
    target = 1

    print 'Starting registration...'
    regstack = stack_register(stack, target)
    print 'Finished registration.'

    for image in range(len(regstack)):
        plt.imshow(regstack[image], interpolation='none')
        plt.waitforbuttonpress()
