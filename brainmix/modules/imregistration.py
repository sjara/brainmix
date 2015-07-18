'''
Image registration.

This module implements the algorithm by Thevenaz et al (1998)
"A Pyramid Approach to Subpixel Registration Based on Intensity"
http://bigwww.epfl.ch/publications/thevenaz9801.pdf

Written by Anna Lakunina and Santiago Jaramillo.
See AUTHORS file for credits.

TO DO:
- FIX BUG: Allow using other downscale factors
- Do we need to keep the masks for points outside the image boundaries?
- We need a citation for the math of the Hessian approximation? (and define what dTheta is)
'''


import numpy as np
import skimage.transform
import scipy.interpolate
import scipy.signal


def rigid_body_transform(image, tfrm):
    '''
    Apply a rigid-body transformation to an image (grayscale), given its spline coefficients.

    Args: 
        image (np.ndarray): grayscale image to transform.
        tfrm (np.ndarray): (3,) transformation [rotation_angle, translation_x, translation_y]

    Returns:
        outimg (np.ndarray): transformed image.
    '''
    skTransform = skimage.transform.SimilarityTransform(rotation=tfrm[0], translation=tfrm[1:])
    outimg = skimage.transform.warp(image, skTransform, order=3, mode='nearest')
    return outimg


def residualsOLD(tfrm, target, source):
    '''
    Compute pixel intensity difference between source and transformed target image.

    Args:
        tfrm (np.ndarray): (3,) transformation [rotation_angle, translation_x, translation_y]
        target (np.ndarray): target (grayscale) image.
        target (np.ndarray): target (grayscale) image.
    Returns:
        err (np.ndarray): intensity difference at each pixel.
    '''
    targettfrm = rigid_body_transform(target, tfrm)
    err = targettfrm-source
    return err


def rigid_body_least_squares(tfrm, target, sgrad, source, maxIterations):
    '''
    Apply modified Levenberg-Marquardt algorithm to minimise the difference in pixel
    intensities between the source and target image samples.

    Args:
        tfrm (np.ndarray): initial tranformation
        tspline (): spline approximation of target image.
        sgrad (np.ndarray): (imHeight,imWidth) gradient of source image 
        
    Returns:

    '''
    imshape = sgrad.shape
    (height, width) = imshape
    attempt = tfrm.copy()
    lambdavar = 1.0
    #err = residuals(-tfrm, target, source)
    err = rigid_body_transform(target, -tfrm) - source
    bestMeanSquares = np.mean(err**2)
    # -- Pre-calculate items for the Hessian (for efficiency) --
    dTheta = sgrad.imag*np.arange(width) - sgrad.real*np.arange(height)[:,np.newaxis]
    dThetaSq = dTheta**2
    dThetaGradReal = dTheta*sgrad.real
    dThetaGradImag = dTheta*sgrad.imag
    gradRealSq = sgrad.real**2
    gradRealGradImag = sgrad.real*sgrad.imag
    gradImagSq = sgrad.imag**2
    (heightSq,widthSq) = np.array(imshape)**2
    iterations = 1
    displacement = 1.0
    # NOTE: using range() for compatibility with Python3
    for iteration in range(maxIterations):
        sHessian = np.array([ [np.sum(dThetaSq), np.sum(dThetaGradReal), np.sum(dThetaGradImag)],
                              [0, np.sum(gradRealSq), np.sum(gradRealGradImag)],
                              [0, 0, np.sum(gradImagSq)] ])
        sHessian += np.triu(sHessian,1).T
        gradient = np.array([np.sum(err*dTheta), 
                             np.sum(err*sgrad.real), 
                             np.sum(err*sgrad.imag)])
        sHessianDiag = np.diag(lambdavar*np.diag(sHessian))
        update = np.dot(np.linalg.inv(sHessian+sHessianDiag),gradient)
        attempt = tfrm - update
        displacement = np.sqrt(update[1]*update[1] + update[2]*update[2]) + \
                       0.25 * np.sqrt(widthSq + heightSq) * np.absolute(update[0])
        iterations += 1
        #err = residuals(-attempt, target, source)
        err = rigid_body_transform(target, -attempt) - source
        if np.mean(err**2)<bestMeanSquares:
            bestMeanSquares = np.mean(err**2)
            # NOTE: Numpy 1.7 or newer has np.copyto() which should be faster than copy()
            tfrm = attempt.copy() # We need to copy values, tfrm=attempt would just make a reference to 'attempt'
            lambdavar /= 10.0 # FIXME: we may need to prevent lambda from becoming 0
        else:
            lambdavar *= 10.0
        if displacement < 0.001:
            break
    return tfrm
            

def rigid_body_registration(source, target, pyramidDepth, minLevel=0, downscale=2, debug=False):
    '''
    Find transformation that registers source image to the target image.

    This function computes the image pyramid for source and target and calculates the transformation
    that minimizes the least-square error between images (starting at the lowest resolution).

    The pyramids consist of downsampled versions of the source and target image, from which the B-spline
    coefficients are computed for the target, and the gradients are computed for the source.
    Note that sometimes it takes a very long time to compute the transformation for the topmost
    layer (containing the full size image) without improving much the registration, so you may want
    to use the parameters below to limit this.

    Args:
        source (np.ndarray): source image, the one that will be transformed.
        target (np.ndarray): target image, the one that will not move.
        pyramidDepth (int): number of pyramid levels, in addition to the original.
        minLevel (int): 0 for original level, >0 for coarser resolution.
    
    Return:
        tfrm (np.ndarray):
    '''
    sourcePyramid = tuple(skimage.transform.pyramid_gaussian(source, max_layer=pyramidDepth, downscale=downscale))
    targetPyramid = tuple(skimage.transform.pyramid_gaussian(target, max_layer=pyramidDepth, downscale=downscale))
    # -- Use Scharr operator to calculate image gradient in horizontal and vertical directions --
    scharr = np.array([[-3-3j, 0-10j, +3-3j], [-10+0j, 0+0j, +10+0j], [-3+3j, 0+10j, +3+3j]])
    tfrm = np.zeros(3)

    for layer in range(pyramidDepth, minLevel-1, -1):
        sourceGradient = scipy.signal.convolve2d(sourcePyramid[layer], scharr, boundary='symm', mode='same')
        imshape = targetPyramid[layer].shape
        tfrm[1:] *= downscale  # Scale translation for next level in pyramid
        tfrm = rigid_body_least_squares(tfrm, targetPyramid[layer], sourceGradient, sourcePyramid[layer], 10*2**(layer-1))
        toptfrm = np.concatenate(([tfrm[0]],tfrm[1:]*pow(downscale,layer)));
        if debug:
            print 'Layer {0}: {1}x{2}'.format(layer,*imshape)
            print 'th={0:0.4}, x={1:0.1f} , y={2:0.1f}'.format(*toptfrm) ### DEBUG
    return toptfrm


if __name__=='__main__':

    import skimage.io
    import matplotlib.pyplot as plt
    
    sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D4-01b.jpg',as_grey=True)
    targetimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D3-01b.jpg',as_grey=True) 

    CASE = 1

    if CASE==0:
        targetimg = skimage.transform.pyramid_reduce(targetimg,2**6)
        #tfrm = np.array([0.6,200,200])
        tfrm = np.array([0.1,2,2])
        #o,m = residuals(tfrm,targetimg,sourceimg)
        o,m = rigid_body_transform(targetimg,tfrm)
        print(o[m].min())
        plt.clf()
        plt.imshow(o, interpolation='none', cmap='CMRmap') #'CMRmap'coolwarm
        plt.gca().set_aspect('equal', 'box')
        plt.colorbar()
        plt.show()

    if CASE==1:
        tfrm = rigid_body_registration(sourceimg, targetimg, 7, 3, debug=True)  # 7,3 works well
        if 0:
            outimg = rigid_body_transform(sourceimg, tfrm)
        else:
            skTransform = skimage.transform.SimilarityTransform(rotation=tfrm[0], translation=tfrm[1:])
            outimg = skimage.transform.warp(sourceimg,skTransform)
            #outimg = skimage.transform.warp(sourceimg,skTransform, order=3, mode='nearest')
        if 1:
            plt.clf()
            plt.imshow(targetimg-outimg, interpolation='none', cmap='coolwarm') #'CMRmap'
            #plt.imshow(outimg, interpolation='none', cmap='coolwarm') #'CMRmap'
            plt.gca().set_aspect('equal', 'box')
            plt.show()

