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

<<<<<<< HEAD
# -- itk -- 
=======
# -- ITK --
>>>>>>> 708fc25a688c90058aefb924c7fbc8ffb92d1413
itkLoaded = True
try:
    import itk
    import itk_affine_registration

    methods.append("ITK Affine")
    functions.append(itk_affine_registration.itk_affine_registration)
   
except ImportError:
    itkLoaded = False
    print "ITK Methods not supported"

<<<<<<< HEAD
# -- thunder --

# ------ #    
=======
>>>>>>> 708fc25a688c90058aefb924c7fbc8ffb92d1413
def get_registration_methods():
    return methods

def get_registration_functions():
    return functions
