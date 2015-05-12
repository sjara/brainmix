'''
Main Qt Window for BrainMix.

Please see the AUTHORS file for credits.
'''

import glob
import os
import numpy as np
from PySide import QtCore 
from PySide import QtGui
import skimage.io
from . import histogram
from . import imageviewer
from ..core import registration_modules
from ..core import data
from ..modules import czifile


class MainWindow(QtGui.QMainWindow):
    def __init__(self, inputdir=None, parent=None):
        '''
        Main window that holds all GUI pieces.
        '''
        super(MainWindow, self).__init__(parent)

        # -- Functional members --
        self.data = data.Data()  # Contains the image data
        self.regActionGroup = QtGui.QActionGroup(self) # Registration actions 

        # -- Widget members --
        self.fitAtStart = True # Fit image to window at start (or not)
        self.imageViewer = imageviewer.ImageViewer(self, fit=self.fitAtStart)
        self.showAligned = False

        # -- Grab the registration methods --
        self.regMethods = registration_modules.get_registration_methods() # List of names
        self.regFunctions = registration_modules.get_registration_functions()
        self.currentRegMethodIndex = None

        # -- Intialize graphical interface --
        self.init_ui()

        # -- Open images if input folder set on command line --
        if inputdir is not None:
            imagefiles = glob.glob(os.path.join(inputdir,'*'))
            self.open_images(imagefiles)
      
    def init_ui(self):
        '''
        Initialize the graphical user interface.
        '''
        self.setWindowTitle('BrainMix')
        self.resize(500, 400)
        self.create_menus()

        # -- Create the central widget and layout --
        mainWidget =  QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        mainWidget.setLayout(layout)
        layout.addWidget(self.imageViewer)
        self.setCentralWidget(mainWidget)

    # -- Signals --  FIXME: Do we need these? And why are they indented this way?
    #signal_image_files = QtCore.Signal( (list,) )
    #signal_volume_file = QtCore.Signal( (str,) ) 

    def set_image(self):
        '''
        Set the current image.
        '''
        #self.imageViewer.set_image(self.data.get_current_image())
        if self.showAligned:
            self.imageViewer.set_image(self.data.get_current_aligned_image())
        else:
            self.imageViewer.set_image(self.data.get_current_image())
        #if self.data.have_aligned():
        #    self.alignedViewer.set_image(self.data.get_current_aligned_image())

    def create_menus(self):
        '''
        Create the application menus.
        '''
        menubar = self.menuBar()
        
        # -- File Menu --
        fileMenu = menubar.addMenu('&File')
        openFilesAction = fileMenu.addAction('&Open images',self.open_images_dialog)
        openFilesAction.setShortcut('Ctrl+O')
        exitAction = fileMenu.addAction('&Quit',self.close)
        exitAction.setShortcut('Ctrl+Q')

        # -- Edit Menu --
        editMenu = menubar.addMenu('&Edit')
        self.editHistogramAct = editMenu.addAction('Edit &histogram', 
                                                   self.slot_edit_histogram)
        self.editHistogramAct.setShortcut('Ctrl+H')

        # -- View Menu --
        viewMenu = menubar.addMenu('&View')
        self.showAlignedAct = QtGui.QAction('Show Aligned', self,checkable=True,
                                            shortcut='Ctrl+a', enabled=False,
                                            triggered=self.slot_show_aligned)
        viewMenu.addAction(self.showAlignedAct)
        viewMenu.addSeparator()
        self.zoomInAct = QtGui.QAction('Zoom In (25%)', self,
                                        shortcut='Ctrl+=',
                                        enabled=True,
                                        triggered=self.slot_zoom_in)
        viewMenu.addAction(self.zoomInAct)
        self.zoomOutAct = QtGui.QAction('Zoom Out (25%)', self,
                                        shortcut='Ctrl+-', enabled=True,
                                        triggered=self.slot_zoom_out)
        viewMenu.addAction(self.zoomOutAct)
        self.fullSizeAct = QtGui.QAction('Full Size', self,
                                        shortcut='Ctrl+N', enabled=True,
                                        triggered=self.slot_full_size)
        viewMenu.addAction(self.fullSizeAct)

        viewMenu.addSeparator()
        self.fitToWindowAct = QtGui.QAction('&Fit to Window', self,
                                            enabled=True, checkable=True,
                                            shortcut='Ctrl+F',
                                            triggered=self.slot_fit_to_window)
        self.fitToWindowAct.setChecked(self.fitAtStart)
        viewMenu.addAction(self.fitToWindowAct)
       
        # -- Registration Menu --
        self.inSubjectAct = QtGui.QAction('In-Subject Registration', self,
                                          enabled=False, triggered=self.slot_register)
        regMenu = menubar.addMenu('Registration')
        methMenu = regMenu.addMenu('Methods')
        for oneRegMethod in self.regMethods:
            act = QtGui.QAction(oneRegMethod, self, checkable=True,
                                triggered=self.slot_switch_reg_methods) 
            methMenu.addAction(act)
            self.regActionGroup.addAction(act)
        if len(self.regMethods)>0:
            self.regActionGroup.actions()[0].setChecked(True)
            #self.savedRegMethod = self.regMethods[0]
            self.currentRegMethodIndex = 0
            self.inSubjectAct.setEnabled(True)
        regMenu.addAction(self.inSubjectAct)
    
    @QtCore.Slot()
    def slot_register(self):
        '''
        Slot for image registration
        '''
        aligned = False
        regFunction = self.regFunctions[self.currentRegMethodIndex]

        # FIXME: at some point we need to remove ITK option
        # FIXME: also, ITK option does not set aligned flag?
        if 'ITK' in self.regMethods[self.currentRegMethodIndex]:
            # -- If this is an itk method, send image filenames --
            self.data.set_aligned_images(regFunction(self.data.get_filenames()))
        else:
            regimages = regFunction(self.data.get_images())
            self.data.set_aligned_images(regimages)
            aligned = True
            self.showAligned = True

        if aligned:
            self.showAlignedAct.setEnabled(True)
            self.showAlignedAct.setChecked(True)
            #self.alignedViewer.set_image(self.data.get_current_aligned_image())
        else:
            print 'No Registation Methods!'

    @QtCore.Slot()
    def slot_switch_reg_methods(self):
        '''Slot for switching registration method'''
        assert len(self.regMethods) > 0
        checkedAction = self.regActionGroup.checkedAction()
        self.currentRegMethodIndex = self.regActionGroup.actions().index(checkedAction)

    @QtCore.Slot()
    def slot_show_aligned(self):
        '''Slot for showing the aligned images'''
        self.showAligned = self.showAlignedAct.isChecked()
        self.set_image()
            
    @QtCore.Slot()
    def slot_fit_to_window(self):
        '''Slot to handle fit to window action callback.'''
        if self.fitToWindowAct.isChecked():
            self.imageViewer.resize_image_to_fit()
        else:
            self.imageViewer.free_size()

    @QtCore.Slot()
    def slot_zoom_in(self):
        self.imageViewer.zoom_in()
        #self.alignedViewer.zoom_in()
        self.fitToWindowAct.setChecked(False)

    @QtCore.Slot()
    def slot_zoom_out(self):
        self.imageViewer.zoom_out()
        #self.alignedViewer.zoom_out()
        self.fitToWindowAct.setChecked(False)

    @QtCore.Slot()
    def slot_full_size(self):
        self.imageViewer.full_size()
        #self.alignedViewer.full_size()
        self.fitToWindowAct.setChecked(False)

    @QtCore.Slot()
    def slot_edit_histogram(self):
        '''Estimate and show histogram.'''
        currentImage = self.data.get_current_image()
        (histValues, binEdges) = np.histogram(currentImage,bins=256)
        #bins = np.arange(256)
        #hist = (20*(np.sin(2*np.pi/100*bins)+2)).astype(int)
        #print np.unique(currentImage)
        # -- Open histogram dialog --
        self.imhist = histogram.HistogramView(histValues,binEdges[:-1])
        print 'Open histogram'
        self.imhist.show()
        #self.imhist.raise()
        #self.imhist.activateWindow()

    def open_images_dialog(self):
        '''
        Brings up a file chooser and signals when files are selected.
        Signal sends file names along.
        Currently supports .jpg and .png
        '''
        files, filtr = QtGui.QFileDialog.getOpenFileNames(self,'Select Input Images',
                                                          '/tmp/','Image Files(*.jpg *.png)')
        self.open_images(files)

    def open_images(self, files):
        '''
        Open images from files
        '''
        if len(files) > 0:
            # -- Save the filenames --
            self.data.set_filenames(files)
            # -- Load in the images --
            imageCollection = skimage.io.ImageCollection(files, as_grey=True, 
                                                         load_func=self.img_load_func)
            if imageCollection[0].dtype=='uint16':
                # FIXME: this assumes 16bit images are really 12bit (true for LISB scope)
                bitdepth = 12
            else:
                bitdepth = 8
            # FIXME: the bitdepth is not used yet by other functions.
            #        We need to use it when converting to QImage
            self.data.set_images(imageCollection.concatenate(),bitdepth=bitdepth)
            # -- Send the first image to the viewer --
            self.imageViewer.initialize(self.data.get_current_image())

    def img_load_func(self,imgfile,as_grey=False):
        '''
        A function that allows loading files of different formats
        '''
        fileName,fileExt = os.path.splitext(imgfile)
        if fileExt.lower() == '.czi':
            czi = czifile.CziFile(imgfile)
            image4D = czi.asarray()
            if as_grey:
                image = image4D[0,:,:,0] # 2D (taking only first channel)
            else:
                raise TypeError('Loading multichannel images has not been implemented.')
                #image = np.rollaxis(image4D,0,3)[:,:,:,0] # 3D
            ###image2D = (image2D/16).astype(np.uint8)
            ### For 3D images: np.rollaxis(image4D,0,3)[:,:,:,0]
            return image
        else:
            return skimage.io.imread(imgfile,as_grey)


    # * * * * * * * EVENTS * * * * * * * *
    def closeEvent(self, event):
        '''
        Executed when closing the main window.
        This method is inherited from QtGui.QMainWindow, which explains
        its camelCase naming.
        '''
        event.accept()
          
    def keyPressEvent(self, event):
        '''
        Catch key presses: forward and backward through image stack.
        '''
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.data.decrement_current_image()
            self.set_image()
        elif key == QtCore.Qt.Key_Right:
            self.data.increment_current_image()
            self.set_image()
        event.accept()
