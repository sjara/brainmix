#!/usr/bin/env python

'''
BrainMix 
Written by Kristi Potter (2015-03-11)
Modified by Santiago Jaramillo (2015-04-10)
'''

import sys
import os
import signal  # To enable Ctrl-C to quit application from terminal
#import optparse # DEPRECATED
import argparse
from PySide import QtGui
sys.path.append("./gui/")
#sys.path.append("./Modules/")
sys.path.append("./core/")

#import .gui #import mainwindow

from gui import mainwindow

"""
# - - - BrainMix - - - 
def BrainMix():
    '''
    DEPRECATED: running the app on the global workspace enables more convenient
                introspection of variables and graphical objects during
                interactive sessions. -- Santiago 2015-04-10
    Main function for BrainMix.
    Function determines if user wants command line or GUI interaction.
    '''    
    # Command Line Parser business:
    parser = optparse.OptionParser()
    parser.add_option("-c", "--command", dest="commandLine",
                      action="store_true", default=False,
                      help="Command Line Interface")
    (options, args) = parser.parse_args()

    # If we don't want a gui, go down command line
    if options.commandLine:
        print "Implement non-gui workflow!"
    # Else, pop up the Qt window
    else:
        signal.signal(signal.SIGINT, signal.SIG_DFL) # Enable Ctrl-C
        app = QtGui.QApplication(sys.argv)
        mainWindow = mainwindow.MainWindow()
        mainWindow.show()
        #sys.exit(app.exec_())
        app.exec_()
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nogui', action='store_true',
                        help='Run application without a Graphical User Interface.')
    args = parser.parse_args()

    if args.nogui:
        print '[brainmix.py] This will run the application with no GUI.'
    else:
        signal.signal(signal.SIGINT, signal.SIG_DFL) # Enable Ctrl-C
        app = QtGui.QApplication(sys.argv)
        mainWindow = mainwindow.MainWindow()
        mainWindow.show()
        sys.exit(app.exec_())

