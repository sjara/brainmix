'''
Module to manage the registration modules.
Add new modules here.

Please see the AUTHORS file for credits.
'''

import sys

# - Load in all registration modules - #
methods = []
functions = []

# -- Dummy (return the original stack) --
def dummy(img_stack): 
    return img_stack
methods.append('Dummy')
functions.append(dummy)

'''
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
'''

# -- thunder --
thunderLoaded = True
try:
    from ..modules import registration 
    methods.append("Thunder Registration")
    functions.append(registration.registration)
except ImportError:
    tunderLoaded = False
    print "Thunder Not loaded"
    raise

# ------ #    

def get_registration_methods():
    return methods

def get_registration_functions():
    return functions
