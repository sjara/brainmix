'''
Main data structure to contain images stacks.

Please see the AUTHORS file for credits.
'''

class Data():
    def __init__(self):
        '''
        Data structure for images
        '''
        self.fileNames = []
        self.images = []
        self.alignedImages = []
        self.nImages = 0
        self.haveAligned = False
        self.bitDepth = None

    def set_filenames(self, files):
        '''Set the names of the image files'''
        self.fileNames = files

    def set_images(self, images, bitdepth=8):
        '''Set the number of images and the original image data'''
        self.nImages = len(images)
        self.images = images
        self.bitDepth = bitdepth

    def set_aligned_images(self, images):
        '''Set the aligned images'''
        self.haveAligned = True
        self.alignedImages = images

    def get_filenames(self):
        '''Return the filenames'''
        return self.fileNames

    def get_num_images(self):
        '''Return the number of images'''
        return self.nImages

    def have_aligned(self):
        '''Return if we have aligned images'''
        return self.haveAligned

    def get_images(self):
        '''Return all of the original images'''
        return self.images

    def get_image(self,ind):
        '''Return all of the original images'''
        return self.images[ind]

    def get_bitdepth(self):
        '''Return all of the original images'''
        return self.bitDepth

    def get_aligned_images(self):
        '''Return all of the aligned images'''
        return self.alignedImages

    def get_aligned_image(self,ind):
        '''Return all of the aligned images'''
        return self.alignedImages[ind]

    # -------------------------------------- #
    # FIXME: Should this be in the Data class?
    """
    def get_current_aligned_image(self):
        '''Return the current aligned image'''
        return self.alignedImages[self.currentImage]

    def get_current_image(self):
        '''Return the current original image'''
        return self.images[self.currentImage]
        
    def increment_current_image(self):
        '''Increment the current image number'''
        self.currentImage += 1
        if self.currentImage == self.nImages:
            self.currentImage = 0

    def decrement_current_image(self):
        '''Decrement the current image number'''
        self.currentImage -= 1
        if self.currentImage < 0:
            self.currentImage = self.nImages-1
    """
