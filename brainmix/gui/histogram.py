'''
Widget to edit the pixel-intensity histogram of images.

Currently this class is intended to do it all:
calculate histogram, show it, edit it.

Please see the AUTHORS file for credits.
'''

from PySide import QtGui
from PySide import QtCore
import numpy as np
from . import multipleslider

class HistogramEditor(QtGui.QWidget):
    def __init__(self,parent=None):
        super(HistogramEditor, self).__init__(parent)
        self.histView = HistogramView()
        self.sliders = multipleslider.MultipleSlider()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.histView)
        layout.addWidget(self.sliders)
        self.setLayout(layout)
 
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+W"), self, self.close,
                        context=QtCore.Qt.WidgetShortcut)

        self.sliders.sliderMoved.connect(self.set_bounds)

    def reset(self,nbins):
        self.sliders.setMaximum(nbins-1)
        self.sliders.setValues([0,nbins-1])
        self.show()
        
    def set_data(self,image,nbins):
        #self.sliders.reset(nbins)
        self.sliders.setMaximum(nbins-1)
        self.histView.set_data(image,nbins)
        #self.set_bounds(0,0)
        #self.set_bounds(1,nbins)

    def set_bounds(self,lowbound,highbound):
        self.histView.set_bounds([lowbound,highbound])


class HistogramView(QtGui.QWidget):
    def __init__(self,parent=None):
        '''
        Intended to show intensity histogram of images.
        It will also show boundaries (to be edited with a slider)
        '''
        super(HistogramView, self).__init__(parent)

        self.hist = []
        self.bins = []

        self.setMinimumWidth(500)
        self.setMinimumHeight(100)
        '''
        self.setMaximumWidth(300)
        self.setMaximumHeight(200)
        '''
        self.boundPos = [16,255-16] # Arbitrary starting point
        self.boundPos = [0,2**16] # Arbitrary starting point

        # -- Paint background (for testing size) --
        if 0:
            self.setAutoFillBackground(True)
            p = self.palette()
            p.setColor(self.backgroundRole(), QtCore.Qt.green)
            self.setPalette(p)

    def set_data(self,image,nbins):
        '''Calculate histogram and show it, given image data'''
        if self.isVisible():
             #FIXME: calculating bins every time may be slow
            if image.dtype==np.float:
                bins = np.linspace(0,1,nbins)
            else:
                bins = np.arange(nbins)
            (histValues, binEdges) = np.histogram(image,bins=bins)
            self.hist = histValues
            self.bins = binEdges[:-1]
            self.update()

    def set_bounds(self,bounds):
        self.boundPos = bounds
        self.update()

    def transform_coords(self,xval,yval):
        '''Transform plotting values to window pixel values'''
        width = self.width()
        height = self.height()
        xvalrange = float(xval[-1]-xval[0])
        yvalrange = float(max(yval))
        hval = (width * (xval-xval[0])/xvalrange).astype(int)
        vval = height-(height * (yval-yval[0])/yvalrange).astype(int)
        return (hval,vval)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        if len(self.bins):
            self.draw_hist(qp)
            self.draw_bound(qp,0)
            self.draw_bound(qp,1)
        qp.end()

    def draw_bound(self,qp,ind):
        '''Draw darkest and brightest level boundaries'''
        boundColor = QtGui.QColor(200,200,220,128)
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(boundColor)
        nBins = len(self.bins)
        width = self.width() * self.boundPos[ind]/nBins
        height = self.height()
        if ind==0:
            qp.drawRect(0,0,width,height)
        elif ind==1:
            qp.drawRect(width,0,self.width(),height)

    def draw_hist(self, qp):
        '''Draw histogram'''
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QtCore.Qt.gray)
        xval = np.r_[self.bins[0],self.bins,self.bins[-1]]
        yval = np.r_[0,self.hist,0]
        hval,vval = self.transform_coords(xval,yval)
        histPoints = QtGui.QPolygonF()
        for oneHval,oneVval in zip(hval,vval):
            histPoints.append(QtCore.QPointF(oneHval,oneVval))
        qp.drawPolygon(histPoints)

''' 
if __name__ == "__main__" and __package__ is None:
    __package__ = "brainmix.gui"
    import sys, signal
    signal.signal(signal.SIGINT, signal.SIG_DFL) # Enable Ctrl-C
    app=QtGui.QApplication.instance() # checks if QApplication already exists 
    if not app: # create QApplication if it doesnt exist 
        app = QtGui.QApplication(sys.argv)
    histeditor = HistogramEditor()
    histeditor.show()
    app.exec_()
'''
