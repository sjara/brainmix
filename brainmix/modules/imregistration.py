'''
Image registration.

This module implements the algorithm by Thevenaz et al (1998)
"A Pyramid Approach to Subpixel Registration Based on Intensity"
http://bigwww.epfl.ch/publications/thevenaz9801.pdf

Written by Anna Lakunina and Santiago Jaramillo.
See AUTHORS file for credits.

TO DO:
- Keep mask for both source and target.
- FIX BUG: Allow using other downscale factors

NOTES:
- rigid-body transformation is faster if most of the resulting image falls outside the range.

- What is dTheta? What reference is used for the math of Hessian?
- Why do we need to find one more attempt at the end?
- Why doesn't it use the diagonal?
'''


import numpy as np
from numpy import math
import skimage.transform
import scipy.interpolate
import scipy.signal


def spline_approx(img):
    '''
    Calculate the spline approximation of an image.

    Args: 
        img (np.ndarray): grayscale image

    Returns:
        spline (scipy.interpolate.RectBivariateSpline): spline approximation of the image.
        coords (np.ndarray): (2,N) array containing the coordinates of each pixel in the image.
    '''
    (height,width) = img.shape
    grid = np.meshgrid(np.arange(width), np.arange(height))
    coords = np.vstack(grid).reshape(2, width*height)
    spline = scipy.interpolate.RectBivariateSpline(np.arange(height), np.arange(width), img)
    return (spline,coords)


def rigid_body_transform(spline, imshape, coords, tfrm):
    '''
    Apply a rigid-body transformation to an image (grayscale), given its spline coefficients.

    Args: 
        spline (scipy.interpolate.RectBivariateSpline): spline approximation of the image.
        imshape (tuple): image size (height, width)
        coords (np.ndarray): (2,N) array containing the coordinates of each pixel in the image.
        tfrm (np.ndarray): (3,) transformation [rotation_angle, translation_x, translation_y]

    Returns:
        outimg (np.ndarray): A transformed image.
    '''
    cosAngle,sinAngle = (math.cos(tfrm[0]),math.sin(tfrm[0]))
    rotMatrix = np.array([ [cosAngle, -sinAngle], [sinAngle, cosAngle] ])
    translationVector = np.array(tfrm[1:])[:,np.newaxis]
    transCoords = np.dot(rotMatrix, coords+translationVector)
    # -- Find coordinates that ended up outside the image --
    outsideX = (transCoords[0,:]<-0.5) | ((transCoords[0,:])>(imshape[1]+0.5))
    outsideY = (transCoords[1,:]<-0.5) | ((transCoords[1,:])>(imshape[0]+0.5))
    outsidePixels = outsideX | outsideY
    flatmask = ~(outsideX | outsideY)
    # -- Evaluate spline at the transformed coordinates --
    img = spline.ev(transCoords[1,flatmask], transCoords[0,flatmask])
    outimg = np.zeros(np.prod(imshape)) # Masked pixels will be zero
    outimg[flatmask] = img
    outimg = outimg.reshape(imshape)
    mask = flatmask.reshape(imshape)
    return (outimg,mask)


def residuals(tfrm, targetspline, source, imshape, coords):
    '''
    Compute pixel intensity difference between source and transformed target image.

    Args:
        tfrm (): ...
        ...
    Returns:
        err (np.ndarray): intensity difference at each pixel.
        mask (np.ndarray): boolean array. False for pixels that should be ignored (outside original image).
                           It is used to compute the gradient and hessian for the next attempt.
    '''
    (targettfrm, mask) = rigid_body_transform(targetspline, imshape, coords, tfrm)
    err = targettfrm-source
    return (err, mask)


def rigid_body_least_squares(tfrm, tspline, sgrad, source, coords, maxIterations):
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
    (err, mask) = residuals(-tfrm, tspline, source, imshape, coords)
    bestMeanSquares = np.mean(err[mask]**2)
    #dTheta = np.multiply(sgrad.imag,np.arange(width)) - np.multiply(sgrad.real,np.arange(height).reshape(height,1))
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
    #while (iterations < maxIterations) and (displacement > 0.001):
    # NOTE: using range() for compatibility with Python3
    for iteration in range(maxIterations):
        sHessian = np.array([ [np.sum(dThetaSq[mask]), np.sum(dThetaGradReal[mask]), np.sum(dThetaGradImag[mask])],
                              [0, np.sum(gradRealSq[mask]), np.sum(gradRealGradImag[mask])],
                              [0, 0, np.sum(gradImagSq[mask])] ])
        sHessian += np.triu(sHessian,1).T
        gradient = np.array([np.sum(err[mask]*dTheta[mask]), 
                             np.sum(err[mask]*sgrad.real[mask]), 
                             np.sum(err[mask]*sgrad.imag[mask])])
        sHessianDiag = np.diag(lambdavar*np.diag(sHessian))
        update = np.dot(np.linalg.inv(sHessian+sHessianDiag),gradient)
        attempt = tfrm - update
        displacement = math.sqrt(update[1]*update[1] + update[2]*update[2]) + \
                       0.25 * math.sqrt(widthSq + heightSq) * np.absolute(update[0])
        iterations += 1
        err, mask = residuals(-attempt, tspline, source, imshape, coords)
        if np.mean(err[mask]**2)<bestMeanSquares:
            bestMeanSquares = np.mean(err[mask]**2)
            # NOTE: Numpy 1.7 or newer has np.copyto() which should be faster than copy()
            tfrm = attempt.copy() # We need to copy values, tfrm=attempt would just make a reference to 'attempt'
            lambdavar /= 10.0 # FIXME: we may need to prevent lambda from becoming 0
        else:
            lambdavar *= 10.0
        if displacement < 0.001:
            break
    '''
    update = np.dot(np.linalg.inv(sHessian),gradient)
    attempt = tfrm - update
    #attempt[0] = tfrm[0] - update[0]
    #attempt[1:] = tfrm[1:] + update[1:]
    err, mask = residuals(attempt*-1, tspline, source, imshape, coords)
    if np.mean(err[mask]**2)<bestMeanSquares:
        tfrm = attempt
    '''
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
        mask
    '''
    #downscale=2
    sourcePyramid = tuple(skimage.transform.pyramid_gaussian(source, max_layer=pyramidDepth, downscale=downscale))
    targetPyramid = tuple(skimage.transform.pyramid_gaussian(target, max_layer=pyramidDepth, downscale=downscale))
    # -- Use Scharr operator to calculate image gradient in horizontal and vertical directions --
    scharr = np.array([[-3-3j, 0-10j, +3-3j], [-10+0j, 0+0j, +10+0j], [-3+3j, 0+10j, +3+3j]])
    tfrm = np.zeros(3)

    for layer in range(pyramidDepth, minLevel-1, -1):
        sourceGradient = scipy.signal.convolve2d(sourcePyramid[layer], scharr, boundary='symm', mode='same')
        imshape = targetPyramid[layer].shape
        (targetSpline,coords) = spline_approx(targetPyramid[layer])
        tfrm[1:] *= downscale  # Scale translation for next level in pyramid
        tfrm = rigid_body_least_squares(tfrm, targetSpline, sourceGradient, sourcePyramid[layer],
                                        coords, 10*2**(layer-1))
        abstfrm = np.concatenate(([tfrm[0]],tfrm[1:]*pow(downscale,layer)));
        if debug:
            print 'Layer {0}: {1}x{2}'.format(layer,*imshape)
            print 'th={0:0.4}, x={1:0.1f} , y={2:0.1f}'.format(*abstfrm) ### DEBUG
    return abstfrm


if __name__=='__main__':

    import skimage.io
    import matplotlib.pyplot as plt
    
    CASE = 1

    if CASE==1:
        sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D3-01b.jpg',as_grey=True)
        targetimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D4-01b.jpg',as_grey=True) 

        tfrm = rigid_body_registration(sourceimg, targetimg, 7, 3, debug=True)  # 7,3 works well

        #skTransform = skimage.transform.SimilarityTransform(rotation=tfrm[0], translation=-tfrm[1:])
        skTransform = skimage.transform.SimilarityTransform(rotation=tfrm[0], translation=tfrm[1:])
        outimg = skimage.transform.warp(sourceimg,skTransform)
        #(spline,coords) = spline_approx(sourceimg)
        #(outimg, mask) = rigid_body_transform(spline, sourceimg.shape, coords, tfrm)

        if 1:
            plt.clf()
            plt.imshow(targetimg-outimg, interpolation='none', cmap='coolwarm') #'CMRmap'
            plt.gca().set_aspect('equal', 'box')
            #plt.axis('equal')
            #plt.colorbar()
            plt.show()

    elif CASE==2:
        sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D3-01b.jpg',as_grey=True)
        (spline,coords) = spline_approx(sourceimg)
        tfrm = [0.1, 800, 900]
        #tfrm = [0, 0, 0]
        outimg = rigid_body_transform(spline, sourceimg.shape, coords, tfrm)
        plt.clf()
        plt.imshow(outimg, interpolation='none', cmap='CMRmap')
        #plt.colorbar()
        plt.axis('equal')
        plt.show()
        
    elif CASE==3:
        sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D3-01b.jpg',as_grey=True)
        tfrm = [0.1, 100, 200]; imshape = sourceimg.shape
        (spline,coords) = spline_approx(sourceimg)

        (height,width) = imshape
        cosAngle,sinAngle = (math.cos(tfrm[0]),math.sin(tfrm[0]))
        rotMatrix = np.array([ [cosAngle, -sinAngle], [sinAngle, cosAngle] ])
        '''
        xShift = rotMatrix[0,0] * tfrm[1] + rotMatrix[0,1] * tfrm[2]
        yShift = rotMatrix[1,0] * tfrm[1] + rotMatrix[1,1] * tfrm[2]
        transVector = np.array([-xShift,-yShift])
        '''
        '''
        transVector = np.dot(rotMatrix,tfrm[1:])
        rotCoords = np.dot(rotMatrix,coords)
        transCoords = rotCoords - transVector[:,np.newaxis]
        '''
        transVector = np.array(tfrm[1:])
        transCoords = np.dot(rotMatrix, coords-transVector[:,np.newaxis])
        outsideX = (transCoords[0,:]<-0.5) | ((transCoords[0,:])>(width+0.5))
        outsideY = (transCoords[1,:]<-0.5) | ((transCoords[1,:])>(height+0.5))
        if 0:
            outsidePixels = outsideX | outsideY
            img = spline.ev(transCoords[1,:], transCoords[0,:])
            outimg = np.multiply(img, ~outsidePixels).reshape(height,width)
        else:
            mask = ~(outsideX | outsideY)
            img = spline.ev(transCoords[1,mask], transCoords[0,mask])
            outimg = np.zeros(height*width)
            outimg[mask] = img
            outimg = outimg.reshape(height,width)
        plt.clf()
        plt.imshow(outimg, interpolation='none', cmap='CMRmap')
        plt.axis('equal')
        plt.show()
        '''
        '''
    elif CASE==4:
        sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D3-01b.jpg',as_grey=True)
        scharr = np.array([[-3-3j, 0-10j, +3-3j], [-10+0j, 0+0j, +10+0j], [-3+3j, 0+10j, +3+3j]])
        grad = scipy.signal.convolve2d(sourceimg, scharr, boundary='symm', mode='same')
        plt.clf()
        plt.imshow(np.abs(grad), interpolation='none', cmap='gray')
        plt.axis('equal')
        plt.show()
    elif CASE==5:
        sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D3-01b.jpg',as_grey=True)
        tform = skimage.transform.SimilarityTransform(scale=1, rotation=0.02,
                                                      translation=[35.7,78.6])
        transImg = skimage.transform.warp(sourceimg,tform)
