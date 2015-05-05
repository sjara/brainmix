#!/usr/bin/env python

'''
BrainMix 
Written by Kristi Potter (2015-03-11)
Modified by Santiago Jaramillo (2015-04-10)
'''

import sys
import os
import signal  # To enable Ctrl-C to quit application from terminal
import argparse
from PySide import QtGui
from brainmix.gui import mainwindow

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
        app = QtGui.QApplication(sys.argv)
        mainWindow = mainwindow.MainWindow(inputdir=args.inputDir)
        mainWindow.show()
        sys.exit(app.exec_())

