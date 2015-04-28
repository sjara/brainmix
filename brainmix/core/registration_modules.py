'''
RegistrationModules.py
Class to manage the registration modules.
Add new modules here.
Written by Kristi Potter, March 2015.
University of Oregon
'''

import sys
sys.path.append("./Modules/")
#from PySide import QtCore 
#from PySide import QtGui


# - Load in all registration modules - #
methods = []
functions = []

# -- ITK --
itkLoaded = True
try:
    import itk
    import itk_affine_registration

    methods.append("ITK Affine")
    functions.append(itk_affine_registration.itk_affine_registration)
   
except ImportError:
    itkLoaded = False
    print "ITK Methods not supported"

# -- thunder --
thunderLoded = True
try:
    import registration 
    methods.append("Thunder Registration")
    functions.append(registration.registration)
    
    #import main
    #methods.append("Rigid")
    #functions.append(main.registration)
    
except ImportError:
    tunderLoaded = False
    print "Thunder Not loaded"

# ------ #    

def get_registration_methods():
    return methods

def get_registration_functions():
    return functions
