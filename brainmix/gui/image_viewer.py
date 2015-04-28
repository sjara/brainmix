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
    def __init__(self, parent = None):
        super(ImageViewer, self).__init__(parent)

        self.scaleFactor = 1.0
        self.fitToWindow = False
        self.origSize = None
        
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtGui.QScrollArea()
        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.setWidget(self.imageLabel);
        self.resize(500, 400)

    # -- Set the image --
    def set_image(self, image):
        
        pixmap = QtGui.QPixmap.fromImage(numpy2qimage.numpy2qimage(image))
        
        self.origSize = pixmap.size()
        self.imageLabel.setPixmap(pixmap)
        self.scaleFactor = 1.0
        if self.fitToWindow:
            self.imageLabel.adjustSize()
            self.resize_image()            
        else:
            self.scale_image(1.0)
      
    # -- Resize event -- 
    def resizeEvent(self, event):
        super(ImageViewer, self).resizeEvent(event)
        if self.fitToWindow:
            self.resize_image()

    # -- Resize the image to be the same width as the scroll area --
    def resize_image(self):
        if self.imageLabel.pixmap() != None:
            pixSize = self.imageLabel.pixmap().size()
            pixSize.scale(self.size()*.9975, QtCore.Qt.KeepAspectRatio)
            self.scaleFactor = float(pixSize.width())/float(self.origSize.width())            
            self.imageLabel.setFixedSize(pixSize)
          
    # -- Zoom in -- 
    def zoom_in(self):
        self.fit_to_window(False)
        self.scale_image(1.25)
        
    # -- Zoom out --
    def zoom_out(self):
        self.fit_to_window(False)
        self.scale_image(0.8)
      
    # -- Full size -- 
    def full_size(self):
        self.fit_to_window(False)
        self.scale_image(1.0/self.scaleFactor)

    # -- Fit in the window -- 
    def fit_to_window(self, fit):
        self.fitToWindow = fit
        self.scrollArea.setWidgetResizable(self.fitToWindow)
        if self.fitToWindow:
            self.resize_image()
        else:
            self.imageLabel.setMaximumSize(QtCore.QSize(16777215, 16777215))
            
    # -- Scale the image -- 
    def scale_image(self, factor):
        if self.imageLabel.pixmap() != None:
            self.scaleFactor *= factor;
            self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size());
            self.adjust_scroll_bars(factor)
       
    # -- Adjust the scroll bars --
    def adjust_scroll_bars(self, factor):
        self.adjust_scroll_bar(self.horizontalScrollBar(), factor);
        self.adjust_scroll_bar(self.verticalScrollBar(), factor);
    def adjust_scroll_bar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))
        
    # -- Catch key press -- 
    def keyPressEvent(self, event):
        '''
        Forward key presses to the parent
        '''
        event.ignore()
