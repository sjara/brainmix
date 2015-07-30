'''
Image registration.

This module implements the algorithm by Thevenaz et al (1998)
"A Pyramid Approach to Subpixel Registration Based on Intensity"
http://bigwww.epfl.ch/publications/thevenaz9801.pdf
with improved convergence by Noppadol Chumchob and Ke Chen (2009)
"A Robust Affine Registration Method"
http://www.math.ualberta.ca/ijnam/Volume-6-2009/No-2-09/2009-02-09.pdf

Written by Anna Lakunina and Santiago Jaramillo.
See AUTHORS file for credits.

TO DO:
- FIX BUG: Allow using other downscale factors
- Do we need to keep the masks for points outside the image boundaries?
'''


import numpy as np
import skimage.transform
import scipy.signal
import scipy.ndimage


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


def rigid_body_least_squares(source, target, tfrm, maxIterations):
    '''
    Apply modified Levenberg-Marquardt algorithm to minimize the difference in pixel
    intensities between the source and target images.

    Args:
        source (np.ndarray): source image, the one that will be transformed.
        target (np.ndarray): target image, the one that will not move.
        tfrm (np.ndarray): (3,) initial transformation [rotation_angle, translation_x, translation_y].

    Returns:
        tfrm (np.ndarray): (3,) best transformation [rotation_angle, translation_x, translation_y].
    '''
    imshape = source.shape
    (height, width) = imshape
    newtfrm = tfrm.copy()
    lambdavar = 1.0
    # -- Use Scharr operator to calculate image gradient in horizontal and vertical directions --
    scharr = np.array([[-3-3j, 0-10j, +3-3j], [-10+0j, 0+0j, +10+0j], [-3+3j, 0+10j, +3+3j]])
    sgrad = scipy.signal.convolve2d(source, scharr, boundary='symm', mode='same')
    # -- Calculate current error --
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
        attempt = newtfrm - update
        displacement = np.sqrt(update[1]*update[1] + update[2]*update[2]) + \
                       0.25 * np.sqrt(widthSq + heightSq) * np.absolute(update[0])
        err = rigid_body_transform(target, -attempt) - source
        if np.mean(err**2)<bestMeanSquares:
            bestMeanSquares = np.mean(err**2)
            # NOTE: Numpy 1.7 or newer has np.copyto() which should be faster than copy()
            newtfrm = attempt.copy() # We need to copy values, tfrm=attempt would just make a reference to 'attempt'
            lambdavar /= 10.0 # FIXME: we may need to prevent lambda from becoming 0
        else:
            lambdavar *= 10.0
        if displacement < 0.001:
            break
    return newtfrm
            

def rigid_body_registration(source, target, pyramidDepth, minLevel=0, downscale=2, debug=False):
    '''
    Find transformation that registers source image to the target image.

    This function computes the image pyramid for source and target and calculates the transformation
    that minimizes the least-square error between images (starting at the lowest resolution).

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
    # -- compute the center of mass for each image to provide the initial guess for the translation --
    scenter = scipy.ndimage.measurements.center_of_mass(sourcePyramid[minLevel])
    tcenter = scipy.ndimage.measurements.center_of_mass(targetPyramid[minLevel])
    tfrm = np.array([0, scenter[0]-tcenter[0], scenter[1]-tcenter[1]])
    print tfrm
    tfrm[1:] /= pow(downscale,pyramidDepth-minLevel)
    #tfrm = np.zeros(3)

    for layer in range(pyramidDepth, minLevel-1, -1):
        tfrm[1:] *= downscale  # Scale translation for next level in pyramid
        tfrm = rigid_body_least_squares(sourcePyramid[layer],targetPyramid[layer],
                                        tfrm, int(10*2**(layer-1)))
        toptfrm = np.concatenate(([tfrm[0]],tfrm[1:]*pow(downscale,layer)));
        if debug:
            print 'Layer {0}: {1}x{2}'.format(layer, *targetPyramid[layer].shape)
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

