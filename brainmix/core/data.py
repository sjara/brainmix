'''
Main data structure to contain images stacks.

Please see the AUTHORS file for credits.
'''

class ImageStack(object):
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
       

