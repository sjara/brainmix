'''
Widget to edit the pixel-intensity histogram of images.


Currently (during development), this class does it all:
calculate histogram, show it, edit it.
'''

from PySide import QtGui
from PySide import QtCore
import numpy as np

class HistogramView(QtGui.QWidget):
    def __init__(self,hist=[],bins=[],parent=None):
        '''
        Intended for histogram on integer-valued data.
        bins should be a sequence of integers (bin centers)

        It will also show boundaries (to be edited with a slider)
        '''
        super(HistogramView, self).__init__(parent)
        self.hist = hist
        self.bins = bins
        self.setMinimumWidth(200)
        self.setMinimumHeight(100)
        self.setMaximumWidth(300)
        self.setMaximumHeight(200)
        self.boundPos = [0,300]

        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+W"), self, self.close,
                        context=QtCore.Qt.WidgetShortcut)

    def set_data(self,image,nbins):
        '''Calculate histogram and show it, given image data'''
        (histValues, binEdges) = np.histogram(image,bins=256)
        self.hist = histValues
        self.bins = binEdges[:-1]
        #bins = np.arange(256)
        #hist = (20*(np.sin(2*np.pi/100*bins)+2)).astype(int)
        #print np.unique(currentImage)
        # -- Open histogram dialog --
        

    def transform_coords(self,xval,yval):
        '''
        Assumes xval[0] = 0
        '''
        width = self.width()
        height = self.height()
        hval = (width*xval/float(xval[-1])).astype(int)
        vval = height-(height*(yval/float(max(yval)))).astype(int)
        return (hval,vval)

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        if len(self.bins):
            self.draw_hist(qp)
            self.draw_bound(qp,1)
        qp.end()

    def draw_bound(self,qp,ind):
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
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QtCore.Qt.gray)
        size = self.size()
        ptf = QtCore.QPointF
        hist = self.hist
        bins = self.bins
        histData = np.vstack((np.r_[0,bins,bins[-1]],
                              np.r_[0,hist,0]))
        xval = np.r_[0,bins,bins[-1]]
        yval = np.r_[0,hist,0]

        hval,vval = self.transform_coords(xval,yval)

        histPoints = QtGui.QPolygonF()
        for oneHval,oneVval in zip(hval,vval):
            histPoints.append(ptf(oneHval,oneVval))
            
        qp.drawPolygon(histPoints)

