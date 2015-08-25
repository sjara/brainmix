import imregistration as imreg
import numpy as np
import matplotlib.pyplot as plt
import skimage.io
from scipy import interpolate

def register_stack(stack, targetInd=0, relative=True):
    '''
    Register a stack of images to each other. A target image is specified that all others will be 
    registered to (the first image if none is specified). The target's neighbors will be registered to
    the target, and then every subsequent image will be registered to its neighbor, resulting in a stack
    of registered images in the same orientation as the target.

    Args: 
        stack (np.ndarray): [nImages, height, width] stack of images for registration.
        targetInd (int): (optional) index of image to be used as first target. Default=0.

    Returns:
        outstack (np.ndarray): [nImages, height, width] stack of registered images.
    '''
    nImages = len(stack)
    outstack = stack.copy() #np.empty(stack.shape)
    pyramidDepth = imreg.get_pyramid_depth(stack[targetInd])
    minLevel = 3 # FIXME: HARDCODED for JaraLab
    print 'Registering stack...'
    for imageInd in range(targetInd-1,-1,-1):
        if relative:
            newTargetInd = imageInd+1
        else:
            newTargetInd = targetInd
        print '{0} to {1}'.format(imageInd,newTargetInd)
        tfrm = imreg.rigid_body_registration(stack[imageInd], outstack[newTargetInd],
                                             pyramidDepth, minLevel)
        outimg = imreg.rigid_body_transform(stack[imageInd], tfrm)
        outstack[imageInd] = outimg
    for imageInd in range(targetInd+1,nImages):
        if relative:
            newTargetInd = imageInd-1
        else:
            newTargetInd = targetInd
        print '{0} to {1}'.format(imageInd,newTargetInd)
        tfrm = imreg.rigid_body_registration(stack[imageInd], outstack[newTargetInd],
                                             pyramidDepth, minLevel)
        outimg = imreg.rigid_body_transform(stack[imageInd], tfrm)
        outstack[imageInd] = outimg
    '''
    if targetInd != len(stack):
        for imageInd in range(targetInd+1, len(stack)):
            print imageInd
            tfrm = imreg.rigid_body_registration(stack[imageInd], outimg, pyramidDepth, minLevel)
            outimg = rigid_body_transform(stack[imageInd], tfrm)
            outstack[imageInd] = outimg
    outimg = stack[targetInd]
    if targetInd != 0:
        for imageInd in reversed(range(targetInd)):
            print imageInd
            tfrm = imreg.rigid_body_registration(stack[imageInd], outimg, pyramidDepth, minLevel)
            outimg = rigid_body_transform(stack[imageInd], tfrm)
            outstack[imageInd] = outimg
        #outstack = outstack[::-1]
        #outstack.extend(outstack2)
    '''
    print 'Done registering stack.'
    return outstack


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
    stack = np.array([img1, img2, img3, img4, img5, img6])
    targetInd = 2

    print 'Starting registration...'
    regstack = register_stack(stack, targetInd, relative=False)
    print 'Finished registration.'

    for image in range(len(regstack)):
        plt.imshow(regstack[image], interpolation='none')
        plt.show()
        plt.waitforbuttonpress()
