'''
Affine image registration.

This module implements the algorithm by Simon Baker and Iain Matthews (2004)
"Lucas-Kanade 20 Years On: A Unifying Framework"
http://www.ri.cmu.edu/pub_files/pub3/baker_simon_2004_1/baker_simon_2004_1.pdf

with improved convergence by Noppadol Chumchob and Ke Chen (2009)
"A Robust Affine Registration Method"
http://www.math.ualberta.ca/ijnam/Volume-6-2009/No-2-09/2009-02-09.pdf


Written by Anna Lakunina and Santiago Jaramillo.
See AUTHORS file for credits.
'''


import numpy as np
from numpy import math
from brainmix.modules import imregistration as imreg
import skimage.transform
import scipy.signal

def affine_transform(image, tfrm):
    '''
    Apply an affine transformation to an image (grayscale).

    Args: 
        image (np.ndarray): original image
        tfrm (np.ndarray): (3,3) homogeneous affine transformation matrix.

    Returns:
        outimg (np.ndarray): A transformed image.
    '''
    skTransform = skimage.transform.AffineTransform(matrix=tfrm)
    outimg = skimage.transform.warp(image, skTransform, order=3, mode='nearest')
    return outimg


def affine_least_squares(source, target, tfrm, maxIterations):
    '''
    Apply modified Levenberg-Marquardt algorithm to minimize the difference in pixel
    intensities between the source and target images.

    Args:
        source (np.ndarray): source image, the one that will be transformed.
        target (np.ndarray): target image, the one that will not move.
        tfrm (np.ndarray): (3,3) initial transformation [homogeneous affine transformation matrix].
        maxIterations (int): maximum number of iterations performed by algorithm before returning a transformation

    Returns:
        tfrm (np.ndarray): (3,3) best transformation.
    '''
    # -- topidentity is used to convert between the standard affine transformation matrix and the one used by this --
    # -- algorithm, which requires the identity transformation to equal zeros(2,3) --
    topidentity = np.vstack((np.eye(2,3),np.zeros(3)))
    imshape = source.shape
    (height, width) = imshape
    newtfrm = tfrm - topidentity
    lambdavar = 1.0
    # -- Use Scharr operator to calculate image gradient in horizontal and vertical directions --
    scharr = np.array([[-3-3j, 0-10j, +3-3j], [-10+0j, 0+0j, +10+0j], [-3+3j, 0+10j, +3+3j]])
    tgrad = scipy.signal.convolve2d(target, scharr, boundary='symm', mode='same')
    # -- Calculate current error --
    err = target - affine_transform(source, tfrm)
    bestMeanSquares = np.mean(err**2)
    # -- Pre-calculate the Hessian --
    xdx = tgrad.real*np.arange(width)
    ydx = tgrad.real*np.arange(height)[:,np.newaxis]
    xdy = tgrad.imag*np.arange(width)
    ydy = tgrad.imag*np.arange(height)[:,np.newaxis]
    (heightSq,widthSq) = np.array(imshape)**2
    displacement = 1.0
    tHessian = np.array([[np.sum(xdx**2), np.sum(xdx*ydx), np.sum(xdx*tgrad.real), np.sum(xdx*xdy), np.sum(xdx*ydy), np.sum(xdx*tgrad.imag)],
                         [0, np.sum(ydx**2), np.sum(ydx*tgrad.real), np.sum(ydx*xdy), np.sum(ydx*ydy), np.sum(ydx*tgrad.imag)],
                         [0, 0, np.sum(tgrad.real**2), np.sum(tgrad.real*xdy), np.sum(tgrad.real*ydy), np.sum(tgrad.real*tgrad.imag)],
                         [0, 0, 0, np.sum(xdy**2), np.sum(xdy*ydy), np.sum(xdy*tgrad.imag)],
                         [0, 0, 0, 0, np.sum(ydy**2), np.sum(ydy*tgrad.imag)],
                         [0, 0, 0, 0, 0, np.sum(tgrad.imag**2)]])
    tHessian += np.triu(tHessian,1).T
    # NOTE: using range() for compatibility with Python3
    for iteration in range(int(maxIterations)):
        gradient = np.array([np.sum(err*xdx),
                             np.sum(err*ydx),
                             np.sum(err*tgrad.real),
                             np.sum(err*xdy),
                             np.sum(err*ydy), 
                             np.sum(err*tgrad.imag)])
        tHessianDiag = np.diag(lambdavar*np.diag(tHessian))
        # -- update is inverted and composed with current best attempt --
        updateinv = np.dot(np.linalg.inv(tHessian+tHessianDiag),gradient).reshape(2,3)
        updateinv = np.vstack((updateinv, np.array([0,0,1])))+topidentity
        update = np.linalg.inv(updateinv)
        newtfrmfull = newtfrm+topidentity
        attempt = np.dot(newtfrmfull,update)
        displacement = np.sqrt(update[0,2]*update[0,2] + update[1,2]*update[1,2]) + \
                       0.25 * np.sqrt(widthSq + heightSq) * np.sum(np.absolute(update[:2,:2]))
        err = target - affine_transform(source, attempt)
        if np.mean(err**2)<bestMeanSquares:
            bestMeanSquares = np.mean(err**2)
            newtfrm = attempt-topidentity
            lambdavar /= 10.0 # FIXME: we may need to prevent lambda from becoming 0
        else:
            lambdavar *= 10.0
        if displacement < 0.001:
            break
    return newtfrm+topidentity
            

def affine_registration(source, target, pyramidDepth, minLevel=0, downscale=2, debug=False):
    '''
    Find affine transformation that registers source image to the target image.

    This function computes the image pyramid for source and target and calculates the transformation
    that minimizes the least-square error between images (starting at the lowest resolution).

    Args:
        source (np.ndarray): source image, the one that will be transformed.
        target (np.ndarray): target image, the one that will not move.
        pyramidDepth (int): number of pyramid levels, in addition to the original.
        minLevel (int): 0 for original level, >0 for coarser resolution.
    
    Return:
        tfrm (np.ndarray): (3,3) best transformation
    '''
    sourcePyramid = tuple(skimage.transform.pyramid_gaussian(source, max_layer=pyramidDepth, downscale=downscale))
    targetPyramid = tuple(skimage.transform.pyramid_gaussian(target, max_layer=pyramidDepth, downscale=downscale))
    # -- compute small scale rigid body transformation to provide the initial guess for the affine transformation --
    rtfrm = imreg.rigid_body_registration(sourcePyramid[minLevel], targetPyramid[minLevel], pyramidDepth-minLevel)
    rotmatrix = np.array([[math.cos(rtfrm[0]), -math.sin(rtfrm[0])], [math.sin(rtfrm[0]), math.cos(rtfrm[0])]])
    tfrm = np.append(rotmatrix, [[rtfrm[1]], [rtfrm[2]]], 1)
    tfrm[:,-1] /= pow(downscale,pyramidDepth-minLevel)
    tfrm = np.vstack((tfrm, [0,0,1]))
    #tfrm = np.array([[1,0,0],[0,1,0],[0,0,1]])
    for layer in range(pyramidDepth, minLevel-1, -1):
        tfrm[:2,-1] *= downscale  # Scale translation for next level in pyramid
        tfrm = affine_least_squares(sourcePyramid[layer],targetPyramid[layer], tfrm, 10*2**(layer-1))
        toptfrm = np.concatenate((tfrm[:2,0:2],tfrm[:2,-1:]*pow(downscale,layer)), axis=1)
        toptfrm = np.vstack((toptfrm, np.array([0,0,1])))
        if debug:
            pass #some debugging stuff Santiago was using
            #print 'Layer {0}: {1}x{2}'.format(layer, *targetPyramid[layer].shape)
            #print 'th={0:0.4}, x={1:0.1f} , y={2:0.1f}'.format(*toptfrm) ### DEBUG
    return toptfrm



if __name__=='__main__':

    import skimage.io
    import matplotlib.pyplot as plt
    
    sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-F1-01b.jpg',as_grey=True)
    #tfrm = np.array([[1.1,-0.5,-20],[0.2,0.9,100]])
    #targetimg = affine_transform(sourceimg, tfrm)
    targetimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-F2-01b.jpg',as_grey=True)
    
    '''sourceimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-F2-01b.jpg',as_grey=True)
    sourceimg = skimage.transform.resize(sourceimg, (320,456))
    #targetimg = skimage.io.imread('/data/brainmix_data/test043_TL/p1-D6-01b.jpg',as_grey=True)
    targetimg = skimage.io.imread('/home/jarauser/data/atlas/ccf25_coronal/ccf25_coronal0238.jpg', as_grey=True)/255.0
    ''''''plt.subplot(1,2,1)
    plt.imshow(sourceimg, cmap='PiYG')
    plt.title('source')
    plt.subplot(1,2,2)
    plt.imshow(targetimg, cmap='PiYG')
    plt.title('target')'''
    
    plt.clf()
    
    CASE = 2
    
    if CASE==0:
        tfrm = affine_least_squares(sourceimg, targetimg, np.eye(2,3), 10)
        outimg = affine_transform(sourceimg, tfrm)
        plt.imshow(outimg)
    
    if CASE == 1:
        tfrm = affine_registration(sourceimg, targetimg, 7, 3, debug=True)
        print tfrm
        outimg1 = affine_transform(sourceimg, tfrm)
        tfrm2 = imreg.rigid_body_registration(sourceimg, targetimg, 7, 3)
        outimg2 = imreg.rigid_body_transform(sourceimg, tfrm2)
        plt.subplot(3,2,1)
        plt.imshow(sourceimg, cmap='PiYG')
        plt.title('source')
        plt.subplot(3,2,2)
        plt.imshow(targetimg, cmap='PiYG')
        plt.title('target')
        plt.subplot(3,2,3)
        plt.imshow(outimg1, cmap='PiYG')
        plt.title('aligned source (affine)')
        plt.subplot(3,2,4)
        plt.imshow(targetimg-outimg1, cmap='PiYG')
        plt.title('difference')
        plt.subplot(3,2,5)
        plt.imshow(outimg2, cmap='PiYG')
        plt.title('aligned source (rigid body)')
        plt.subplot(3,2,6)
        plt.imshow(targetimg-outimg2, cmap='PiYG')
        plt.title('difference')
        
    if CASE == 2:
        tfrm = affine_registration(sourceimg, targetimg, 7, 3)
        print tfrm
        outimg = affine_transform(sourceimg, tfrm)
        plt.subplot(2,2,1)
        plt.imshow(sourceimg, cmap='PiYG')
        plt.title('source')
        plt.subplot(2,2,2)
        plt.imshow(targetimg, cmap='PiYG')
        plt.title('target')
        plt.subplot(2,2,3)
        plt.imshow(outimg, cmap='PiYG')
        plt.title('aligned source')
        plt.subplot(2,2,4)
        plt.imshow(targetimg-outimg, cmap='PiYG')
        plt.title('difference')
    

    
