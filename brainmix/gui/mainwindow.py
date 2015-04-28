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

        if len(self.regMethods) != 0:
            self.savedRegMethod = self.regMethods[0]
        else:
            self.savedRegMethod = None
            
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
        self.zoomInAct = QtGui.QAction("Zoom In (25%)", self,
                                        shortcut="Ctrl+=",
                                        enabled=True,
                                        triggered=self.slot_zoom_in)
        viewMenu.addAction(self.zoomInAct)
        self.zoomOutAct = QtGui.QAction("Zoom Out (25%)", self,
                                        shortcut="Ctrl+-", enabled=True,
                                        triggered=self.slot_zoom_out)
        viewMenu.addAction(self.zoomOutAct)
        self.fullSizeAct = QtGui.QAction("Full Size", self,
                                        shortcut="Ctrl+n", enabled=True,
                                        triggered=self.slot_full_size)
        viewMenu.addAction(self.fullSizeAct)

        
        viewMenu.addSeparator()
        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                                            enabled=True, checkable=True,
                                            shortcut="Ctrl+F",
                                            triggered=self.slot_fit_to_window)
        viewMenu.addAction(self.fitToWindowAct)
       
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
    
    # -- Slot for image registration --
    @QtCore.Slot()
    def slot_register(self):
        
        aligned = False
        for i in range(0, len(self.regMethods)):
                if self.savedRegMethod == self.regMethods[i]:

                    # If this is an itk method, send image filenames
                    if "ITK" in self.savedRegMethod:
                        self.data.set_aligned_images(self.regFunctions[i](self.data.get_filenames()))
                    else:
                        print "here"
                        images = self.regFunctions[i](self.data.get_images())
                        print "done"
                        self.data.set_aligned_images(images)
                    aligned = True

        if aligned:
            self.alignedViewer.set_image(self.data.get_current_aligned_image())
        else:
            print "No Registation Methods!"

    # -- Slot for switching registration method --
    @QtCore.Slot()
    def slot_switch_reg_methods(self):
        if len(self.regMethods) == 0:
            return
        
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

    # -- Slot for zoom in --
    @QtCore.Slot()
    def slot_zoom_in(self):
        self.imageViewer.zoom_in()
        self.alignedViewer.zoom_in()
        self.fitToWindowAct.setChecked(False)

    # -- Slot for zoom out --
    @QtCore.Slot()
    def slot_zoom_out(self):
        self.imageViewer.zoom_out()
        self.alignedViewer.zoom_out()
        self.fitToWindowAct.setChecked(False)

    # -- Slot for full size --
    @QtCore.Slot()
    def slot_full_size(self):
        self.imageViewer.full_size()
        self.alignedViewer.full_size()
        self.fitToWindowAct.setChecked(False)
 
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
            #self.data.set_images(skimage.io.ImageCollection(files, as_grey=True).concatenate())
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
            self.set_image()
        elif key == QtCore.Qt.Key_Right:
            self.data.increment_current_image()
            self.set_image()
        event.accept()
