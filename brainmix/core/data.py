'''
Main data structure to contain images stacks.

Please see the AUTHORS file for credits.
'''

import copy
import os

class ImageStackOLD(object):
    def __init__(self):
        '''Data structure for images'''
        self.fileNames = []
        self.images = []
        self.nImages = 0
        self.bitDepth = None
    def set_images(self, images, bitdepth=None):
        '''Set the number of images and the original image data'''
        self.nImages = len(images)
        self.images = images
        if bitdepth is not None: 
            self.bitDepth = bitdepth
    def set_filenames(self, files):
        '''Set the names of the image files'''
        self.fileNames = files
    def copy(self):
        return copy.deepcopy(self)

'''        
# QUESTION: why do we need an Image object instead of Slice having attributes
#           for images and filenames as lists?
class SliceOLD(object):
    def __init__(self):
        self.images = [] # List of data.Image objects
        self.transformation = [] # Transformation for registration
    def add_image(self):
        pass
    def get_channels(self):
        channels = [img.label for img in self.images]
        return channels
class ImageOLD(object):
     def __init__(self,data,filename,label):
        self.data = data
        self.filename = filename
        self.label = label
        #self.bitDepth # Should this be a list with bitDepth for each channel/image
###thisImage = Image(images[indimg],filename,channelThisImg)
###self.slices[indSlice].images.append(thisImage)
'''

class Slice(object):
    def __init__(self):
        self.images = [] # List of 2D np.ndarray objects
        self.filenames = [] # List of strings. 
        self.labels = [] # List of strings. Label for each image (e.g., what channel)
        self.transformation = [] # Transformation for registration (1D or 2D array)
    def add_image(self, data, filename, label):
        self.images.append(data)
        self.filenames.append(filename)
        self.labels.append(label)


class ImageStack(list):
    def __init__(self):
        '''This object is a list of data.Slice objects to store images of different channels for each slice'''
        #self.slices = [] # List of data.Slice objects (which contain image data)
        #self.nSlices = 0
        #self.bitDepth = None
    def set_images(self, images, filenames):
        '''Set the number of images and the original image data'''
        possibleChannels = ['b','r','g']
        prevSliceLabel = ''
        indSlice = -1
        for indimg,filename in enumerate(filenames):
            basename = os.path.splitext(os.path.basename(filename))
            channelThisImg = basename[0][-1]
            if prevSliceLabel != basename[0][:-1]:
                self.append(Slice())
                indSlice += 1
                prevSliceLabel = basename[0][:-1]
            #self.slices[indSlice].add_image(images[indimg],filename,channelThisImg)
            self[indSlice].add_image(images[indimg],filename,channelThisImg)
    def get_filenames(self):
        '''Get the names of the image files'''
        print 'Not implemented'
    def copy(self):
        print 'Not implemented'
        pass
        #return copy.deepcopy(self)

