'''
The classes defined here will contain a session
(parameters, pointers to data and algorithms, stage of processing, etc).

Please see the AUTHORS file for credits.
'''

import glob
import os
import skimage.io
import skimage.exposure
from . import data
from ..core import registration_modules
from ..modules import czifile

class Session(object):
    def __init__(self, inputdir=None):
        '''Application session'''
        self.origImages = data.ImageStack()
        self.alignedImages = data.ImageStack()
        self.editedImages = data.ImageStack()
        self.currentImageInd = 0
        self.aligned = False
        self.edited = False
        self.loaded = False

        # -- Grab the registration methods --
        self.regMethods = registration_modules.get_registration_methods() # List of names
        self.regFunctions = registration_modules.get_registration_functions()
        self.currentRegMethodIndex = None

        # -- Open images if input folder set on command line --
        if inputdir is not None:
            imagefiles = glob.glob(os.path.join(inputdir,'*'))
            self.open_images(imagefiles)
            self.loaded = True

    def get_current_image(self, aligned=False):
        '''Return current image'''
        # FIXME: There should be edited for orig and for aligned
        if self.edited:
            return self.editedImages.images[self.currentImageInd]
        elif aligned:
            return self.alignedImages.images[self.currentImageInd]
        else:
            return self.origImages.images[self.currentImageInd]

    def set_registration_method(self,regMethodIndex):
        '''Set the registration method by index'''
        self.currentRegMethodIndex = regMethodIndex

    def open_images(self, files):
        '''Open images from files'''
        if len(files) > 0:
            # -- Load in the images --
            imageCollection = skimage.io.ImageCollection(files, as_grey=True, 
                                                         load_func=self.img_load_func)
            if imageCollection[0].dtype=='uint16':
                # FIXME: this assumes 16bit images are really 12bit (true for LISB scope)
                bitdepth = 12
            else:
                
                bitdepth = 8
            # FIXME: the bitdepth is not used yet by other functions.
            #        We need to use it when converting to QImage
            self.origImages.set_images(imageCollection.concatenate(),bitdepth=bitdepth)
            self.editedImages = self.origImages.copy()
            self.alignedImages.bitDepth = bitdepth # FIXME: maybe the bitdepth is different
            # -- Save the filenames --
            self.origImages.set_filenames(files)

    def img_load_func(self,imgfile,as_grey=False):
        '''
        A function that allows loading files of different formats
        '''
        fileName,fileExt = os.path.splitext(imgfile)
        if fileExt.lower() == '.czi':
            czi = czifile.CziFile(imgfile)
            image4D = czi.asarray()
            if as_grey:
                image = image4D[0,:,:,0] # 2D (taking only first channel)
            else:
                raise TypeError('Loading multichannel images has not been implemented.')
                #image = np.rollaxis(image4D,0,3)[:,:,:,0] # 3D
            ###image2D = (image2D/16).astype(np.uint8)
            ### For 3D images: np.rollaxis(image4D,0,3)[:,:,:,0]
            return image
        else:
            #return skimage.io.imread(imgfile,as_grey)
            return (256*skimage.io.imread(imgfile,as_grey)).astype('uint8') # FIXME: it should be 255

    def increment_current_image(self):
        '''Increment the current image number'''
        self.currentImageInd += 1
        if self.currentImageInd == self.origImages.nImages:
            self.currentImageInd = 0

    def decrement_current_image(self):
        '''Decrement the current image number'''
        self.currentImageInd -= 1
        if self.currentImageInd < 0:
            self.currentImageInd = self.origImages.nImages-1

    def register_stack(self):
        '''Apply registration algorithm to image stack'''
        regFunction = self.regFunctions[self.currentRegMethodIndex]
        regImages = regFunction(self.origImages.images)
        self.alignedImages.set_images(regImages)
        aligned = True

    def change_levels(self,levels):
        '''Adjust intensity of pixels'''
        ind = self.currentImageInd
        self.edited = True
        self.editedImages.images[ind,:,:] = \
            skimage.exposure.rescale_intensity(self.origImages.images[ind,:,:],levels)
        #print '[session.py]'
        #print levels
        #print self.editedImages.images[ind,:,:].min(), self.editedImages.images[ind,:,:].max()

def change_pixel_levels(image,levels):
    '''Adjust pixel intensity so that  '''
