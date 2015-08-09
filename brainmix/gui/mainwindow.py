'''
Main Qt Window for BrainMix.

Please see the AUTHORS file for credits.
'''

#import numpy as np
from PySide import QtCore 
from PySide import QtGui
from . import histogram
from . import imageviewer

class MainWindow(QtGui.QMainWindow):
    # -- Create signals --
    #updateImage = QtCore.Signal(int) # Send the image index
    #setRegistrationMethod = QtCore.Signal(int) # Set registration method by index

    def __init__(self, session=None, parent=None):
        '''Main window that holds all GUI pieces.'''
        super(MainWindow, self).__init__(parent)

        # -- Functional members --
        self.session = session
        self.regActionGroup = QtGui.QActionGroup(self) # Registration actions 
        self.fitAtStart = True # Fit image to window at start (or not)

        # -- Widget members --
        self.imageViewer = imageviewer.ImageViewer(self, fit=self.fitAtStart)
        self.imhist = histogram.HistogramEditor() # If parent=self, it will be non-window child
        
        # -- Intialize graphical interface --
        self.init_ui()

        # -- If session already has images, show them --
        if session.loaded:
            # FIXME: initialization should be automatic inside imageViewer
            #        maybe by checking a flag (reset when loading data)
            self.imageViewer.initialize(self.session.get_current_image())
            self.set_image()

        # -- Connect signals --
        self.imhist.sliders.sliderMoved.connect(self.change_levels)

    def change_levels(self,lowbound,highbound):
        self.session.change_levels((lowbound,highbound))
        self.set_image()

    def update_title(self):
        nImages = len(self.session.filenames)
        if nImages:
            currentInd = self.session.currentImageInd
            currentFilename = self.session.filenames[currentInd]
            self.setWindowTitle('BrainMix - {0} ({1}/{2})'.format(currentFilename,currentInd+1,nImages))
        else:
            self.setWindowTitle('BrainMix')

    def init_ui(self):
        '''Initialize the graphical user interface.'''
        self.update_title()
        self.resize(500, 400)
        self.create_menus()

        # -- Create the central widget and layout --
        mainWidget =  QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        mainWidget.setLayout(layout)
        layout.addWidget(self.imageViewer)
        self.setCentralWidget(mainWidget)

    def set_image(self):
        '''Set the current image.'''
        if self.showAlignedAct.isChecked():
            self.imageViewer.set_image(self.session.get_current_image(aligned=True))
        else:
            self.imageViewer.set_image(self.session.get_current_image())
        self.update_title()

    def create_menus(self):
        '''Create the application menus.'''
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
                                                   self.open_histogram)
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
                                        triggered=self.imageViewer.zoom_in)
        viewMenu.addAction(self.zoomInAct)
        self.zoomOutAct = QtGui.QAction('Zoom Out (25%)', self,
                                        shortcut='Ctrl+-', enabled=True,
                                        triggered=self.imageViewer.zoom_out)
        viewMenu.addAction(self.zoomOutAct)
        self.origSizeAct = QtGui.QAction('Original Size (1:1)', self,
                                        shortcut='Ctrl+N', enabled=True,
                                        triggered=self.imageViewer.original_size)
        viewMenu.addAction(self.origSizeAct)

        viewMenu.addSeparator()
        self.fitToWindowAct = QtGui.QAction('&Fit to Window', self,
                                            enabled=True,
                                            shortcut='Ctrl+F',
                                            triggered=self.imageViewer.fit_to_window)
        viewMenu.addAction(self.fitToWindowAct)
       
        # -- Registration Menu --
        self.inSubjectAct = QtGui.QAction('In-Subject Registration', self,
                                          enabled=False, 
                                          shortcut='Ctrl+R',
                                          triggered=self.slot_register)
        regMenu = menubar.addMenu('&Registration')
        methMenu = regMenu.addMenu('Methods')
        for oneRegMethod in self.session.regMethods:
            act = QtGui.QAction(oneRegMethod, self, checkable=True,
                                triggered=self.slot_switch_reg_methods) 
            methMenu.addAction(act)
            self.regActionGroup.addAction(act)
        if len(self.session.regMethods)>0:
            self.regActionGroup.actions()[0].setChecked(True)
            self.session.set_registration_method(0)
            self.inSubjectAct.setEnabled(True)
        regMenu.addAction(self.inSubjectAct)
    
    @QtCore.Slot()
    def slot_register(self):
        '''Slot for image registration'''
        self.session.register_stack()
        self.set_image()
        self.showAlignedAct.setEnabled(True)
        self.showAlignedAct.setChecked(True)

    @QtCore.Slot()
    def slot_switch_reg_methods(self):
        '''Slot for switching registration method'''
        assert len(self.session.regMethods) > 0
        checkedAction = self.regActionGroup.checkedAction()
        currentRegMethodIndex = self.regActionGroup.actions().index(checkedAction)
        self.session.set_registration_method(currentRegMethodIndex)

    @QtCore.Slot()
    def slot_show_aligned(self):
        '''Slot for showing the aligned images'''
        # The method self.set_image will know if showAligned has been checked.
        self.set_image()
            
    def open_histogram(self):
        '''Open histogram widget.'''
        #self.imhist.show()
        # FIXME: this is repeated in update_histogram
        #bitDepth = self.session.get_current_bitdepth()
        bitDepth = self.session.origImages.bitDepth
        self.imhist.reset(2**bitDepth)
        self.update_histogram()

    def update_histogram(self):
        '''Estimate and update histogram.'''
        currentImage = self.session.get_current_image()
        bitDepth = self.session.origImages.bitDepth
        self.imhist.set_data(currentImage,2**bitDepth)

    def open_images_dialog(self):
        '''Brings up a file chooser.'''
        files, filtr = QtGui.QFileDialog.getOpenFileNames(self,'Select Input Images',
                                                          '/tmp/','Image Files(*)')
        self.session.open_images(files)
        self.imageViewer.initialize(self.session.get_current_image())

    def closeEvent(self, event):
        '''
        Executed when closing the main window.
        This method is inherited from QtGui.QMainWindow, which explains
        its camelCase naming.
        '''
        self.imhist.close()
        event.accept()
          
    def keyPressEvent(self, event):
        '''
        Catch key presses: forward and backward through image stack.
        '''
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.session.decrement_current_image()
            self.set_image()
            # FIXME: maybe this should send a signal (e.g., to update histogram)
            #self.updateImage.emit()
            self.update_histogram()
        elif key == QtCore.Qt.Key_Right:
            self.session.increment_current_image()
            self.set_image()
            self.update_histogram()
        event.accept()
