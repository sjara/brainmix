#!/usr/bin/env python

'''
BrainMix 
Written by Kristi Potter
March 11, 2015
'''

import sys, os
from optparse import OptionParser
from PySide import QtGui
sys.path.append("./gui/")
#sys.path.append("./Modules/")
sys.path.append("./core/")

#import .gui #import mainwindow

from gui import mainwindow

# - - - BrainMix - - - 
def BrainMix():
    '''
    Main function for BrainMix.
    Function determines if user wants command line or GUI interaction.
    '''    
    # Command Line Parser business:
    parser = OptionParser()
    parser.add_option("-c", "--command", dest="commandLine",
                      action="store_true", default=False,
                      help="Command Line Interface")
    (options, args) = parser.parse_args()

    # If we don't want a gui, go down command line
    if options.commandLine:
        print "Implement non-gui workflow!"
    # Else, pop up the Qt window
    else:
        app = QtGui.QApplication(sys.argv)
        mainWindow = mainwindow.MainWindow()
        mainWindow.show()
        sys.exit(app.exec_())
    
if __name__ == '__main__':
    BrainMix()
