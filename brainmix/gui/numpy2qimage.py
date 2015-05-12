'''
Functions to convert from an ndarray to a QImage.
Modified from:
http://femr.googlecode.com/hg-history/e06e4336439755f075dc693acaffb72093fd8c45/src/contrib/qimage2ndarray.py
'''
import numpy as numpy
from PySide import QtGui

# -- Convert from ndarray to QImage --
def numpy2qimage(array):
    if numpy.ndim(array) == 2:
        return gray2qimage(array)
    elif numpy.ndim(array) == 3:
        return rgb2qimage(array)
    raise ValueError("can only convert 2D or 3D arrays")

def gray2qimage(gray):
    '''
    Convert numpy array to QtImage
    '''
    if len(gray.shape) != 2:
        raise ValueError("gray2QImage can only convert 2D arrays")

    h, w = gray.shape
    if gray.dtype == numpy.uint8:
        gray = numpy.require(gray, numpy.uint8, 'C')
        result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
        result.ndarray = gray
        for i in range(256):
            result.setColor(i, QtGui.QColor(i, i, i).rgb())
    elif gray.dtype == numpy.uint16:
        # This assumes that a 16bit image is only 12bit resolution: 2^16-2^12=16
        gray = (gray/16).astype(numpy.uint8)
        gray = numpy.require(gray, numpy.uint8, 'C')
        h, w = gray.shape
        result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
        result.ndarray = gray
        #for i in range(256):
        #    result.setColor(i, QtGui.QColor(i, i, i).rgb())
    else:
        # Convert by multiplying by 256 and making it uint8
        gray = (gray * 256).astype(numpy.uint8)
        gray = numpy.require(gray, numpy.uint8, 'C')
        h, w = gray.shape
        result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
        result.ndarray = gray
        for i in range(256):
            result.setColor(i, QtGui.QColor(i, i, i).rgb())
    return result


def OLDgray2qimage(gray):
    """Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
    colormap.  The first dimension represents the vertical image axis.
    
    ATTENTION: This QImage carries an attribute `ndimage` with a
    reference to the underlying numpy array that holds the data. On
    Windows, the conversion into a QPixmap does not copy the data, so
    that you have to take care that the QImage does not get garbage
    collected (otherwise PyQt will throw away the wrapper, effectively
    freeing the underlying memory - boom!)."""   
    if len(gray.shape) != 2:
        raise ValueError("gray2QImage can only convert 2D arrays")

    # If the type is not numpy.uint8, then convert by multiplying by 256
    if type(gray[0][0]) == numpy.float64:      
        gray = (gray * 256).astype(numpy.uint8)

    gray = numpy.require(gray, numpy.uint8, 'C')
    h, w = gray.shape
    result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
    result.ndarray = gray
    for i in range(256):
        result.setColor(i, QtGui.QColor(i, i, i).rgb())
    return result
    
def rgb2qimage(rgb):
    """Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
    have three dimensions with the vertical, horizontal and RGB image axes.
    
    ATTENTION: This QImage carries an attribute `ndimage` with a
    reference to the underlying numpy array that holds the data. On
    Windows, the conversion into a QPixmap does not copy the data, so
    that you have to take care that the QImage does not get garbage
    collected (otherwise PyQt will throw away the wrapper, effectively
    freeing the underlying memory - boom!)."""
    if len(rgb.shape) != 3:
        raise ValueError("rgb2QImage can only convert 3D arrays")
    if rgb.shape[2] not in (3, 4):
        raise ValueError("rgb2QImage can expects the last dimension to contain exactly three (R,G,B) or four (R,G,B,A) channels")

    h, w, channels = rgb.shape

    # Qt expects 32bit BGRA data for color images:
    bgra = numpy.empty((h, w, 4), numpy.uint8, 'C')
    bgra[...,0] = rgb[...,2]
    bgra[...,1] = rgb[...,1]
    bgra[...,2] = rgb[...,0]
    if rgb.shape[2] == 3:
        bgra[...,3].fill(255)
        fmt = QtGui.QImage.Format_RGB32
    else:
        bgra[...,3] = rgb[...,3]
        fmt = QtGui.QImage.Format_ARGB32

    result = QtGui.QImage(bgra.data, w, h, fmt)
    result.ndarray = bgra
    return result

