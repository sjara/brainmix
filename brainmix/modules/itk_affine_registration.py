'''
itk_affine_registration.py
Written by: Areej Alghamdi and Kristi Potter
University of Oregon
Adopted from: http://itk.org/Wiki/ITK/Examples/Registration/ImageRegistrationMethodAffine
Date: 2/19/15
Purpose: Registers a volume of images using itk (affine). Based on the c++ examples, translated to python.
Input:   imageVolume (skimage.io.ImageCollection) : the volume of images to align.
Output:

'''
import sys, os
import warnings
warnings.filterwarnings("ignore")
import itk
import numpy as np
import skimage.io

class Registrator():
    
    # -- init --
    def __init__(self, parent = None):
        
        print "Initialize"
        self.newVolume = []
        self.outputImageFilenames = []
        self.count = 1

        # Image dimensions
        pixelType = itk.UC
        Dimension = 2

        # This line is what takes so long
        self.ImageType = itk.Image[pixelType, Dimension]
        self.ReaderType = itk.ImageFileReader[self.ImageType]
        
        # The transform that will map the fixed image into the moving image.
        TransformType = itk.AffineTransform[itk.D, Dimension]
        OptimizerType = itk.RegularStepGradientDescentOptimizer
        MetricType = itk.MeanSquaresImageToImageMetric[self.ImageType, self.ImageType]
        InterpolatorType = itk.LinearInterpolateImageFunction[self.ImageType, itk.D]
        RegistrationType = itk.ImageRegistrationMethod[self.ImageType, self.ImageType]
        
        # Create the components
        metric = MetricType.New()
        transform = TransformType.New()
        optimizer = OptimizerType.New()
        interpolator = InterpolatorType.New()
        self.registration = RegistrationType.New()

        self.registration.SetMetric( metric )
        self.registration.SetTransform( transform )
        self.registration.SetInterpolator( interpolator )
        
        # Configure the optimizer
        optimizer.SetMaximumStepLength( .1 )
        optimizer.SetMinimumStepLength( 0.01 )
        optimizer.SetNumberOfIterations( 200 )
        self.registration.SetOptimizer( optimizer )

        # Configure the transform
        initialParameters = transform.GetParameters()
        self.registration.SetInitialTransformParameters( initialParameters )

        ResampleFilterType = itk.ResampleImageFilter[self.ImageType,self.ImageType]
        self.resampler = ResampleFilterType.New()
        
        self.CastFilterType = itk.CastImageFilter[self.ImageType,self.ImageType]

        self.fixedImageReader = self.ReaderType.New()
        self.fixedImage = self.ImageType.New()

        self.movingImageReader = self.ReaderType.New()
        self.movingImage = self.ImageType.New()
        
    def set_fixed_image(self, fileName):
        print "Set Fixed Image:", fileName
        fileName = fileName.encode('ascii','ignore')
        self.fixedImageReader.SetFileName(fileName)
        self.fixedImageReader.Update()
        self.fixedImage = self.fixedImageReader.GetOutput()
        self.registration.SetFixedImage( self.fixedImage )
        self.registration.SetFixedImageRegion( self.fixedImage.GetLargestPossibleRegion() )
        self.resampler.SetSize( self.fixedImage.GetLargestPossibleRegion().GetSize() )
        self.resampler.SetOutputOrigin ( self.fixedImage.GetOrigin() )
        self.resampler.SetOutputSpacing( self.fixedImage.GetSpacing() )
        self.resampler.SetOutputDirection( self.fixedImage.GetDirection())
        self.resampler.SetDefaultPixelValue( 100 )
        
    def register(self, movingFileName):
        print "Register:", movingFileName
        movingFileName = movingFileName.encode('ascii','ignore')
        
        self.movingImageReader.SetFileName(movingFileName)
        self.movingImageReader.Update()
        self.movingImage = self.movingImageReader.GetOutput()
        
        self.registration.SetMovingImage( self.movingImage )
        self.registration.Update()

        self.resampler.SetInput( self.movingImage )
        self.resampler.SetTransform( self.registration.GetOutput().Get() )
     
        caster = self.CastFilterType.New()
        caster.SetInput( self.resampler.GetOutput() )
      
        WriterType = itk.ImageFileWriter[self.ImageType]
        writer = WriterType.New()

        alignedImage = "itk_affine_aligned_image%d.jpg" % self.count
        self.outputImageFilenames.append(alignedImage)
        writer.SetFileName( alignedImage ) 
        self.count += 1
        writer.SetInput( caster.GetOutput() )
        writer.Update()
        
        
# - - module template function - - #
def itk_affine_registration(imageFilenames):
    '''
    This registration module takes in a list of filename files,
    and return a list of output images. Registers all images to
    the first one.
    '''
    print "ITK Affine Registration Module."
  
    
    # Set up the registrator class and call registration
    r = Registrator()
    fixedImage = imageFilenames[0]
    r.set_fixed_image(fixedImage)
    for i in range(1, len(imageFilenames)):
        r.register(imageFilenames[i])

    # Read in the output images
    outputFiles = r.outputImageFilenames
    outputFiles.insert(0, fixedImage)
    outImages = []
    for i in outputFiles:
        outImages.append(skimage.io.imread(i))

    # Delete the side-effect images
    for i in r.outputImageFilenames:
        os.remove(i)
        
    # Return the ndarray of image data
    return outImages
