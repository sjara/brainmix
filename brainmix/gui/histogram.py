'''
Widget to edit the pixel-intensity histogram of images.
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
        self.nBins = len(bins)
        #self.setMinimumWidth(200)
        #self.setMinimumHeight(100)
        #self.setMaximumWidth(300)
        #self.setMaximumHeight(200)
        self.boundPos = [100,200]

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
        self.draw_hist(qp)
        self.draw_bound(qp,1)
        qp.end()

    def draw_bound(self,qp,ind):
        boundColor = QtGui.QColor(200,200,220,128)
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(boundColor)
        width = self.width() * self.boundPos[ind]/self.nBins
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
