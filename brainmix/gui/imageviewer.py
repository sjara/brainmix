'''
Image viewer rotates through a series of images

Please see the AUTHORS file for credits.
'''
import sys
from PySide import QtCore 
from PySide import QtGui
from . import numpy2qimage

class ImageViewer(QtGui.QScrollArea):
    def __init__(self, parent = None):
        '''
        Widget to view a stack of images
        '''
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
        self.initialized = False

    def set_image(self, image):
        '''
        Set the current image
        '''
        pixmap = QtGui.QPixmap.fromImage(numpy2qimage.numpy2qimage(image))
        if not self.initialized:
            self.origSize = pixmap.size()
            self.scaleFactor = 1.0
        self.imageLabel.setPixmap(pixmap)
        if not self.initialized:
            if self.fitToWindow:
                self.imageLabel.adjustSize()
                self.resize_image()            
            else:
                self.scale_image(self.scaleFactor)
            self.initialized = True
       
    def resizeEvent(self, event):
        super(ImageViewer, self).resizeEvent(event)
        if self.fitToWindow:
            self.resize_image()

    def resize_image(self):
        '''Resize the image to be the same width as the scroll area'''
        if self.imageLabel.pixmap() is not None:
            pixSize = self.imageLabel.pixmap().size()
            # FIXME: What factor to use (or pixels to subtract) to use the full window?
            pixSize.scale(self.size()*.9975, QtCore.Qt.KeepAspectRatio)
            self.scaleFactor = float(pixSize.width())/float(self.origSize.width())            
            self.imageLabel.setFixedSize(pixSize)
          
    def zoom_in(self):
        self.fit_to_window(False)
        self.scale_image(1.25)
        
    def zoom_out(self):
        self.fit_to_window(False)
        self.scale_image(0.8)
      
    def full_size(self):
        self.fit_to_window(False)
        self.scale_image(1.0/self.scaleFactor)


    ############ I GOT THIS FAR (SJ 20150508) ##########

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
