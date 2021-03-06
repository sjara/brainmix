#!/usr/bin/env python

'''
BrainMix 

Please see the AUTHORS file for credits.
'''

import sys
import os
import signal  # To enable Ctrl-C to quit application from terminal
import argparse
from PySide import QtGui
from brainmix.gui import mainwindow
from brainmix.core import session
reload(mainwindow) # During development
reload(session) # During development

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nogui', action='store_true',
                        help='Run application without a Graphical User Interface.')
    parser.add_argument('-i', action='store', dest='inputDir',
                        help='Directory containing images to open on startup.')
    args = parser.parse_args()

    if args.nogui:
        print '[brainmix.py] This will run the application with no GUI.'
    else:
        signal.signal(signal.SIGINT, signal.SIG_DFL) # Enable Ctrl-C
        app=QtGui.QApplication.instance() # checks if QApplication already exists 
        if not app: # create QApplication if it doesnt exist 
            app = QtGui.QApplication(sys.argv)
        mainSession = session.Session(inputdir=args.inputDir)
        mainWindow = mainwindow.MainWindow(mainSession)
        mainWindow.show()
        sys.exit(app.exec_())

