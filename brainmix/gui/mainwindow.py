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
        self.imhist = histogram.HistogramView()
        
        # -- Intialize graphical interface --
        self.init_ui()

        # -- If session already has images, show them --
        if session.loaded:
            # FIXME: initialize should be automatic inside imageViewer
            #        maybe by checking a flag (reset when loading data)
            self.imageViewer.initialize(self.session.get_current_image())
            self.set_image()

    def init_ui(self):
        '''Initialize the graphical user interface.'''
        self.setWindowTitle('BrainMix')
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
        self.fitToWindowAct.setChecked(False)

    @QtCore.Slot()
    def slot_zoom_out(self):
        self.imageViewer.zoom_out()
        self.fitToWindowAct.setChecked(False)

    @QtCore.Slot()
    def slot_full_size(self):
        self.imageViewer.full_size()
        self.fitToWindowAct.setChecked(False)

    @QtCore.Slot()
    def slot_edit_histogram(self):
        '''Estimate and show histogram.'''
        currentImage = self.session.get_current_image()
        bitDepth = self.session.origImages.bitDepth
        '''
        (histValues, binEdges) = np.histogram(currentImage,bins=256)
        #bins = np.arange(256)
        #hist = (20*(np.sin(2*np.pi/100*bins)+2)).astype(int)
        #print np.unique(currentImage)
        '''
        # -- Open histogram dialog --
        self.imhist.set_data(currentImage,bitDepth)
        self.imhist.update() # FIXME: necessary because if it's open it won't update
        self.imhist.show()


    def open_images_dialog(self):
        '''
        Brings up a file chooser and signals when files are selected.
        Signal sends file names along.
        Currently supports .jpg and .png
        '''
        files, filtr = QtGui.QFileDialog.getOpenFileNames(self,'Select Input Images',
                                                          '/tmp/','Image Files(*.jpg *.png)')
        self.session.open_images(files)
        self.imageViewer.initialize(self.session.get_current_image())


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
            self.session.decrement_current_image()
            self.set_image()
            # FIXME: maybe this should send a signal (e.g., to update histogram)
            #self.updateImage.emit()
            #self.slot_edit_histogram()
        elif key == QtCore.Qt.Key_Right:
            self.session.increment_current_image()
            self.set_image()
            #self.slot_edit_histogram()
        event.accept()
