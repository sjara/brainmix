'''
Main Qt Window for BrainMix.

Written by
Kristi Potter 2014-08-27
University of Oregon
'''
from PySide import QtCore 
from PySide import QtGui

import image_viewer

import skimage.io
from core import registration_modules
from core import data

#- - - Main Window that holds all GUI pieces - - -#
class MainWindow(QtGui.QMainWindow):

    # -- init --
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        # Functional members
        self.data = data.Data()
        self.regActs = []

        # Widget members
        self.imageViewer = image_viewer.ImageViewer(self)
        self.alignedViewer = image_viewer.ImageViewer(self)

        # Grab the registration methods
        self.regMethods = registration_modules.get_registration_methods()
        self.regFunctions = registration_modules.get_registration_functions()
        self.savedRegMethod = self.regMethods[0]
        
        # Intialize 
        self.init_ui()
      
    # -- Initialize the user interface --
    def init_ui(self):

        self.setWindowTitle("BrainMix")
        self.resize(500, 400)

        self.create_menus()

        # Create a group box and the layout
        groupBox =  QtGui.QGroupBox()
        layout = QtGui.QHBoxLayout()
        groupBox.setLayout(layout)
        layout.addWidget(self.imageViewer)
        layout.addWidget(self.alignedViewer)

        # Set the groupbox as the central window
        self.setCentralWidget(groupBox)

    # -- Signals --
    signal_image_files = QtCore.Signal( (list,) )
    signal_volume_file = QtCore.Signal( (str,) ) 

    # -- Set the current image --
    def set_image(self):
        self.imageViewer.set_image(self.data.get_current_image())
        if self.data.have_aligned():
            self.alignedViewer.set_image(self.data.get_current_aligned_image())

    # -- Create the menus --
    def create_menus(self):
        menubar = self.menuBar()
        
        # File Menu
        fileMenu = menubar.addMenu('&File')
        openFilesAction = fileMenu.addAction('&Open images',self.open_images)
        openFilesAction.setShortcut('Ctrl+O')
        exitAction = fileMenu.addAction('&Quit',self.close)
        exitAction.setShortcut('Ctrl+Q')

        # View Menu
        viewMenu = menubar.addMenu('View')
        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                                            enabled=True, checkable=True,
                                            shortcut="Ctrl+F",
                                            triggered=self.slot_fit_to_window)
        viewMenu.addAction(self.fitToWindowAct)
        self.zoomInAct = QtGui.QAction("Zoom In (25%)", self,
                                        shortcut="Ctrl+=",
                                        enabled=True,
                                        triggered=self.slot_zoom_in)
        viewMenu.addAction(self.zoomInAct)
        self.zoomOutAct = QtGui.QAction("Zoom Out (25%)", self,
                                        shortcut="Ctrl+-", enabled=True,
                                        triggered=self.slot_zoom_out)
        viewMenu.addAction(self.zoomOutAct)
        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                                            shortcut="Ctrl+S", enabled=True,
                                            triggered=self.slot_normal_size)
        viewMenu.addAction(self.normalSizeAct)

        # Registration Menu
        regMenu = menubar.addMenu('Registration')
        methMenu = regMenu.addMenu('Methods')
        self.regActions = QtGui.QActionGroup(self)
        for i in self.regMethods:
            act = QtGui.QAction(i, self, checkable=True, triggered=self.slot_switch_reg_methods) 
            self.regActs.append(act)
            methMenu.addAction(act)
            self.regActions.addAction(act)
            
        self.regAct = regMenu.addAction("In-Subject Registration", self.slot_register)
        
    # -- Update the action --
    def update_actions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    # -- Slot for image registration --
    @QtCore.Slot()
    def slot_register(self):
        for i in range(0, len(self.regMethods)):
                if self.savedRegMethod == self.regMethods[i]:

                    # If this is an itk method, send image filenames
                    if "ITK" in self.savedRegMethod:
                        self.data.set_aligned_images(self.regFunctions[i](self.data.get_filenames()))
                    else:
                        self.data.set_aligned_images(self.regFunctions[i](self.data.get_images()))
        self.alignedViewer.set_image(self.data.get_current_aligned_image())


    # -- Slot for switching registration method --
    @QtCore.Slot()
    def slot_switch_reg_methods(self):
        for i in range(0, len(self.regActs)):
            if self.regActs[i].isChecked():
                self.savedRegMethod = self.regMethods[i]
                break    
        
    # -- Slot for fit to window --
    @QtCore.Slot()
    def slot_fit_to_window(self):
        '''
        Slot to handle fit to window action callback.
        '''
        if self.fitToWindowAct.isChecked():
            self.imageViewer.fit_to_window(True)
            self.alignedViewer.fit_to_window(True)
        else:
            self.imageViewer.fit_to_window(False)
            self.alignedViewer.fit_to_window(False)
        self.update_actions();

    # -- Slot for zoom in --
    @QtCore.Slot()
    def slot_zoom_in(self):
        self.imageViewer.zoom_in()
        self.alignedViewer.zoom_in()

    # -- Slot for zoom out --
    @QtCore.Slot()
    def slot_zoom_out(self):
        self.imageViewer.zoom_out()
        self.alignedViewer.zoom_out()

    # -- Slot for normal size --
    @QtCore.Slot()
    def slot_normal_size(self):
        self.imageViewer.normal_size()
        self.alignedViewer.normal_size()
 
    # -- Open images --
    def open_images(self):
        '''
        Brings up a file chooser and signals when files are selected.
        Signal sends file names along.
        Currently supports .jpg and .png
        '''
        files, filtr = QtGui.QFileDialog.getOpenFileNames(self,
                                                          "Select Input Images",
                                                          "/Users/kpotter/Data/Mouse/",
                                                          "Image Files(*.jpg *.png)")
        if len(files) > 0:
            
            # Save the filenames
            self.data.set_filenames(files)

            # Load in the images
            self.data.set_images(skimage.io.ImageCollection(files).concatenate())
        
            # Send the first image to the viewer
            self.imageViewer.set_image(self.data.get_current_image())

    # * * * * * * * EVENTS * * * * * * * *
    # -- Event on close --
    def closeEvent(self, event):
        '''
        Executed when closing the main window.
        This method is inherited from QtGui.QMainWindow, which explains
        its camelCase naming.
        '''
        event.accept()
          
    # -- Catch key press -- 
    def keyPressEvent(self, event):
        '''
        Forward key presses
        '''
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.data.decrement_current_image()
        elif key == QtCore.Qt.Key_Right:
            self.data.increment_current_image()
        self.set_image()

        event.accept()