#!/usr/bin/env python
'''
module_template.py
Written by: Kristi Potter
Date: 1/20/15
Purpose: template for all jaraAnnote modules.
In this comment section, the purpose and approach
for each module should be described in full. In
addition, any dependencies, reference materials,
papers, etc, should be documented. Implementation-
specific notes should be documented in the comments.

Input: note all inputs to the function including
       type and default values.
       parameter1: string, required.
       parameter2: string, optional, default = None
Output: note all output, including any auxillary
        data or log files.
        output: none.
'''
import sys, os

# - - module template function - - #
def moduleTemplate(parameter1, parameter2=None):
    '''
    Here you can add any other comments necessary for this module, including
    what other functions are called and usages, etc.
    '''

    # Print the parameters
    print "Module Template!! Write New Module!"
    print "First parameter: ", parameter1
    print "Second parameter: ", parameter2

    # Call the subfunction
    module_sub_function()

# - - subfunction - - #
def module_sub_function():
    '''
    detail what this function does
    '''
    print "You can also add in a subfunction, or we can change things to a class if necessary."

## -- Wrap main so we can call this via command line OR from another file -- ##
if __name__ == '__main__':

    p1 = None
    p2 = None
    
    if len(sys.argv) > 1: 
        p1 = sys.argv[0]
    if len(sys.argv) > 2:
        p2 = sys.argv[1]
    
    # for ease, we are assuming parameters from the command line are in the
    # same order as the function
    moduleTemplate(p1, p2)
