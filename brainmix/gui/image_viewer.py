'''
Image viewer rotates through a series of images
Kristi Potter 2014-08-27
University of Oregon
'''
import sys
from PySide import QtCore 
from PySide import QtGui
import numpy2qimage

# - - - Widget to view a series of images - - -
class ImageViewer(QtGui.QScrollArea):
  
    # -- init --
    def __init__(self, parent = None):#, data = None):
        super(ImageViewer, self).__init__(parent)
        self.scaleFactor = 0.0
        self.resize(500,400)
        self.fitToWindow = False
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.init_widget()
      
    # -- Initialize the widget --
    def init_widget(self):
        '''
        Initialize widgets for displaying the images.
        '''
        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                                      QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.setWidget(self.imageLabel)
        self.normal_size()

    # -- Update the image to display --
    def set_image(self, image):
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(numpy2qimage.numpy2qimage(image)))
        self.scaleFactor = 1.0;
        if not self.fitToWindow:
            self.imageLabel.adjustSize()
        
    # -- Scale the image
    def scale_image(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())
 
        self.adjust_scroll_bar(self.horizontalScrollBar(), factor)
        self.adjust_scroll_bar(self.verticalScrollBar(), factor)

    # -- Adjust the scroll -- 
    def adjust_scroll_bar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                            + ((factor - 1) * scrollBar.pageStep()/2)))
    # -- Zoom in -- 
    def zoom_in(self):
        self.scale_image(1.25)

    # -- Zoom out --
    def zoom_out(self):
        self.scale_image(0.8)

    # -- Normal size -- 
    def normal_size(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    # -- Fit in the window -- 
    def fit_to_window(self, fit):
        
        #self.fitToWindow = not self.fitToWindow
        self.setWidgetResizable(fit)
        if not fit: 
            self.normal_size()
