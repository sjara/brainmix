'''
Image registration.

This module implements the algorithm by Thevenaz et al (1998)
"A Pyramid Approach to Subpixel Registration Based on Intensity"
http://bigwww.epfl.ch/publications/thevenaz9801.pdf

Written by Anna Lakunina and Santiago Jaramillo.
See AUTHORS file for credits.

== TO DO ==
- Mask according to something besides black pixels.
- In rigidBodyTransform, apply transform only to pixels inside.

== NOTES ==
- rigid-body transformation is faster if most of the resulting image falls outside the range.

== COMMENTS ==
- What is scharr? is it to calculate the first gradient?
  is there an advantage in doing it as a complex number instead of two convolutions?
- Docstrings https://sphinxcontrib-napoleon.readthedocs.org/en/latest/
- Naming conventions. Functions/methods should be lowercase (with underscores)
- I changed the mask to a boolean mask (not by value anymore).
- In residual() I removed the mask on the source. Maybe we need it later for a stack.
- attempt = tfrm; attempt[0] = tfrm[0] - update[0] (THIS WILL CHANGE tfrm)
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
    transCoords = np.dot(rotMatrix, coords-translationVector)  # NOTE: translation is subtracted
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
    Compute the difference in intensity of each pixel between the source image and a transformed target image.

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


def pyramidLMA(source, target, pyramidDepth, minLevel=0):
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
    downscale=2
    sourcepyramid = tuple(skimage.transform.pyramid_gaussian(source, max_layer=pyramidDepth, downscale=downscale))
    targetpyramid = tuple(skimage.transform.pyramid_gaussian(target, max_layer=pyramidDepth, downscale=downscale))
    scharr = np.array([[-3-3j, 0-10j, +3-3j], [-10+0j, 0+0j, +10+0j], [-3+3j, 0+10j, +3+3j]])
    tfrm = np.zeros(3)

    for layer in range(pyramidDepth, minLevel-1, -1):
        imgradient = scipy.signal.convolve2d(sourcepyramid[layer], scharr, boundary='symm', mode='same')
        imshape = targetpyramid[layer].shape
        print 'Layer {0}: {1}x{2}'.format(layer,*imshape)
        (spline,coords) = spline_approx(targetpyramid[layer])
        tfrm[1:] *= downscale
        tfrm = rigidBodyLeastSquares(tfrm, spline, imgradient, sourcepyramid[layer], coords, imshape, 10*2**(layer-1))
        abstfrm = np.concatenate(([tfrm[0]],tfrm[1:]*pow(downscale,layer)));
        print 'th={0:0.4}, x={1:0.1f} , y={2:0.1f}'.format(*abstfrm) ### DEBUG
    tfrm[1:] *= pow(downscale,minLevel)
    return tfrm


def rigidBodyLeastSquares(tfrm, spline, grad, source, coords, imshape, maxIterations):
    '''
    
    This method applies the inverted Levenberg-Marquardt algorithm to minimise the difference in pixel
    intensities between the source and target image samples.
    '''
    (height, width) = imshape
    #print maxIterations
    attempt = tfrm
    lambdavar = 1.0
    (err, mask) = residuals(-tfrm, spline, source, imshape, coords)
    bestMeanSquares = np.mean(err[mask]**2)
    dTheta = np.multiply(grad.imag,np.arange(width)) - np.multiply(grad.real,np.arange(height).reshape(height,1))
    iterations = 1
    while True:
        hessian = np.array([[np.sum(dTheta[mask]**2), np.sum(dTheta[mask]*grad.real[mask]), np.sum(dTheta[mask]*grad.imag[mask])], [0, np.sum(grad.real[mask]**2), np.sum(grad.real[mask]*grad.imag[mask])], [0, 0, np.sum(grad.imag[mask]**2)]])
        hessian += np.triu(hessian,1).T
        gradient = np.array([np.sum(err[mask]*dTheta[mask]), np.sum(err[mask]*grad.real[mask]), np.sum(err[mask]*grad.imag[mask])])
        hessiandiag = np.array(np.multiply(lambdavar*np.identity(3),hessian))
        update = np.dot(np.linalg.inv(hessian+hessiandiag),gradient)
        attempt[0] = tfrm[0] - update[0]
        #attempt[1] = math.cos(update[0]) * (tfrm[1]+update[1]) - math.sin(update[0]) * (tfrm[2] + update[2])
        #attempt[2] = math.sin(update[0]) * (tfrm[1]+update[1]) + math.cos(update[0]) * (tfrm[2] + update[2])
        attempt[1:] = tfrm[1:] + update[1:]
        #attempt = tfrm - update
        displacement = math.sqrt(update[1]**2 + update[2]**2) + 0.25 * math.sqrt(width**2 + height**2) * np.absolute(update[0])
        #print update
        #print lambdavar
        iterations += 1
        err, mask = residuals(attempt*-1, spline, source, imshape, coords)
        if np.mean(err[mask]**2)<bestMeanSquares:
            bestMeanSquares = np.mean(err[mask]**2)
            tfrm = attempt
            lambdavar /= 10.0 #todo: possibly hack to prevent lambda from becoming 0
        else:
            lambdavar *= 10.0
        if iterations > maxIterations or displacement < 0.001:
            break
    update = np.dot(np.linalg.inv(hessian),gradient)
    attempt[0] = tfrm[0] - update[0]
    attempt[1:] = tfrm[1:] + update[1:]
    #attempt = tfrm - update
    err, mask = residuals(attempt*-1, spline, source, imshape, coords)
    if np.mean(err[mask]**2)<bestMeanSquares:
        tfrm = attempt
    return tfrm
            



if __name__=='__main__':

    import skimage.io
    import matplotlib.pyplot as plt
    
    CASE = 1

    if CASE==1:
        sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D3-01b.jpg',as_grey=True)
        targetimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D4-01b.jpg',as_grey=True) 

        tfrm = pyramidLMA(sourceimg, targetimg, 7, 3)  # 7,3 works well

        skTransform = skimage.transform.SimilarityTransform(rotation=tfrm[0], translation=-tfrm[1:])
        outimg = skimage.transform.warp(sourceimg,skTransform)
        #(spline,coords) = spline_approx(sourceimg)
        #(outimg, mask) = rigid_body_transform(spline, sourceimg.shape, coords, tfrm)

        if 1:
            plt.clf()
            plt.imshow(targetimg-outimg, interpolation='none', cmap='coolwarm') #'CMRmap'
            plt.axis('equal')
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
