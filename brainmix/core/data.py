'''
Data Structure, so far...
Written by
Kristi Potter 2014-08-29
University of Oregon
'''

# - - - Data structure for our images - - -
class Data():
    
    # -- init --
    def __init__(self):
        self.fileNames = []
        self.images = []
        self.alignedImages = []
        self.numImages = 0
        self.haveAligned = False
        
        self.currentImage = 0 # ?? Should this be here or in the GUI?
       
    # -- Set the names of the image files --
    def set_filenames(self, files):
        self.fileNames = files

    # -- Set the number of images and the original image data --
    def set_images(self, images):
        self.numImages = len(images)
        self.images = images

    # -- Set the aligned images --
    def set_aligned_images(self, images):
        self.haveAligned = True
        self.alignedImages = images

    # -- Return the filenames -- 
    def get_filenames(self):
        return self.fileNames

    # -- Return the number of images --
    def get_num_images(self):
        return self.numImages

    # -- Return if we have aligned images --
    def have_aligned(self):
        return self.haveAligned

    # -- Return all of the original images --
    def get_images(self):
        return self.images

    # -- Return all of the aligned images --
    def get_aligned_images(self):
        return self.alignedImages


    # -------------------------------------- #
    # ?? -- Should this be in Data -- ??
    # -- Return the current aligned image --
    def get_current_aligned_image(self):
        return self.alignedImages[self.currentImage]

    # -- Return the current original image --
    def get_current_image(self):
        return self.images[self.currentImage]

    # -- Increment the current image number --
    def increment_current_image(self):
        self.currentImage += 1
        if self.currentImage == self.numImages:
            self.currentImage = 0

    # -- Decrement the current image number --
    def decrement_current_image(self):
        self.currentImage -= 1
        if self.currentImage < 0:
            self.currentImage = self.numImages-1
