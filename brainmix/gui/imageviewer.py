'''
Image viewer rotates through a series of images

Please see the AUTHORS file for credits.
'''
import sys
from PySide import QtCore 
from PySide import QtGui
from . import numpy2qimage

class ImageViewer(QtGui.QScrollArea):
    def __init__(self, parent=None, fit=True):
        '''
        Widget to view a stack of images.

        ImageViewer contains a QLabel in which the image is painted.
        This QLabel will change size according to the user's commands.

        PARAMETERS:
        fit: [Boolean] start with image fit to window or not.
        '''
        super(ImageViewer, self).__init__(parent)
        self.scaleFactor = 1.0
        self.fitToWindow = fit
        self.origSize = None
        
        # -- Values to be used for panning with mouse --
        self.mousePos = None
        self.hScrollValue = None
        self.vScrollValue = None

        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        #self.imageLabel.setAlignment(QtCore.Qt.AlignCenter) # FIXME: Does not align image to scroll area

        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.setWidget(self.imageLabel)
        self.resize(500, 400)
        self.initialized = False

    def initialize(self, image):
        '''Grab size of loaded images.'''
        self.set_image(image)
        self.origSize = self.imageLabel.pixmap().size()
        self.resizeEvent(None) # Necessary to show initial image with correct size

    def set_image(self, image):
        '''Set the current image'''
        # FIXME: the conversion to QPixmap is done everytime
        #        would it be better/faster to keep all pixmaps in memory?
        pixmap = QtGui.QPixmap.fromImage(numpy2qimage.numpy2qimage(image))
        self.imageLabel.setPixmap(pixmap)

    def resizeEvent(self, event):
        super(ImageViewer, self).resizeEvent(event)
        if self.fitToWindow:
            self.fit_to_window()

    def zoom_in(self):
        self.free_size()
        self.scale_image(1.25)
        
    def zoom_out(self):
        self.free_size()
        self.scale_image(0.8)
      
    def original_size(self):
        '''Resize image to original size'''
        self.free_size()
        self.scale_image(1.0/self.scaleFactor)

    def free_size(self):
        '''Unfix size of image. To be used for zooming.'''
        self.fitToWindow = False
        # FIXME: Harcoded numbers. What Qt constant contains these numbers?
        self.imageLabel.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.imageLabel.setMinimumSize(QtCore.QSize(0,0)) # Fixes issue #11

    def fit_to_window(self):
        '''Resize the image to be the same width as the scroll area'''
        self.fitToWindow = True
        if self.imageLabel.pixmap() is not None:
            pixSize = self.imageLabel.pixmap().size()
            # FIXME: What factor to use (or pixels to subtract) to use the full window?
            pixSize.scale(self.size()*.995, QtCore.Qt.KeepAspectRatio)
            self.scaleFactor = float(pixSize.width())/float(self.origSize.width())            
            self.imageLabel.setFixedSize(pixSize)
          
    def scale_image(self, factor):
        if self.imageLabel.pixmap() is not None:
            self.scaleFactor *= factor;
            self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size());
            self.adjust_scroll_bars(factor) # To keep centered when zooming
       
    def adjust_scroll_bars(self, factor):
        self.adjust_scroll_bar(self.horizontalScrollBar(), factor);
        self.adjust_scroll_bar(self.verticalScrollBar(), factor);

    def adjust_scroll_bar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))
       
    def keyPressEvent(self, event):
        '''Forward key presses to the parent'''
        event.ignore() # Necessary to let the parent take care of key events

    def mousePressEvent(self, event):
        self.mousePos = event.globalPos()
        self.hScrollValue = self.horizontalScrollBar().value()
        self.vScrollValue = self.verticalScrollBar().value()
        
    def mouseMoveEvent(self, event):
        if event.buttons()==QtCore.Qt.LeftButton:
            newpos = self.mousePos-event.globalPos()
            vbar = self.verticalScrollBar()
            vbar.setValue(self.vScrollValue+newpos.y())
            hbar = self.horizontalScrollBar()
            hbar.setValue(self.hScrollValue+newpos.x())

    def wheelEvent(self, event):
        '''Capture mouse-wheel events (e.g., for zooming)'''
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            if event.delta()>0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            event.ignore()
        #self.emit(SIGNAL('scroll(int)'), ev.delta())
