'''
Slider with multiple handles

http://code.qt.io/cgit/qt/qt.git/tree/src/gui/widgets/qslider.cpp

Please see the AUTHORS file for credits.
'''

from PySide import QtCore 
from PySide import QtGui


class MultipleSlider(QtGui.QSlider):
    ### OLDsliderMoved = QtCore.Signal(int,int) # Send handle and position
    sliderMoved = QtCore.Signal(int,int) # Send each position
    # FIXME: what if we want more handles? how do we pass a list or change the number of args?

    '''Multiple slider'''
    def __init__(self, nsliders=2):
        super(MultipleSlider, self).__init__(orientation=QtCore.Qt.Orientation.Horizontal)
        self._nsliders=2
        self._pos = []
        self.active_slider = 0

        self.reset(256)
        #self.appStyle = QtGui.QApplication.style() 
        #self.optList = self._nsliders*[QtGui.QStyleOptionSlider()]
        # NOTE: this doesn't work. It looks like all instances of QStyleOptionSlider
        #       point to the same.

    def reset(self,nbins):
        self.setMaximum(nbins)
        self._pos = [0,nbins] # FIXME: change to [0,nbins]
        #self.sliderMoved.emit(0,self._pos[0])
        #self.sliderMoved.emit(1,self._pos[1])
        self.sliderMoved.emit(*self._pos)

    def setValues(self,values):
        self._pos = values
        self.update()

    def setValue(self,sliderID,value):
        self._pos[sliderID] = value
        self.update()

    def getValue(self,sliderID):
        return self._pos[sliderID]
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        style = QtGui.QApplication.style() 
        opt = QtGui.QStyleOptionSlider()
        for indh, value in enumerate(self._pos):
            self.initStyleOption(opt)
            if indh==0:
                opt.subControls = QtGui.QStyle.SC_SliderGroove | QtGui.QStyle.SC_SliderHandle
            else:
                opt.subControls = QtGui.QStyle.SC_SliderHandle
            opt.sliderPosition = self._pos[indh]
            opt.sliderValue = self._pos[indh]
            style.drawComplexControl(QtGui.QStyle.CC_Slider, opt, painter, self)

    def mousePressEvent(self, event):
        if event.button()==QtCore.Qt.MouseButton.LeftButton:
            event.accept()
            style = QtGui.QApplication.style() 
            opt = QtGui.QStyleOptionSlider()
            for indh, value in enumerate(self._pos):
                self.initStyleOption(opt)
                opt.sliderPosition = value                
                hit = style.hitTestComplexControl(style.CC_Slider, opt, event.pos(), self)
                if hit == style.SC_SliderHandle:
                    self.active_slider = indh
                    self.pressedControl = hit
                    self.triggerAction(self.SliderMove)
                    self.setRepeatAction(self.SliderNoAction)
                    self.setSliderDown(True)
                    break
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.pressedControl != QtGui.QStyle.SC_SliderHandle:
            event.ignore()
            return
        event.accept()
        opt = QtGui.QStyleOptionSlider()
        self.initStyleOption(opt)
        sliderLength = self.style().pixelMetric(QtGui.QStyle.PM_SliderSpaceAvailable, opt, self)
        posValue = event.pos().x()
        posValue -= 8 # Hack to align mouse to handle
        newPos = QtGui.QStyle.sliderValueFromPosition(self.minimum(),self.maximum(),posValue,sliderLength)
        ###print self.minimum(),self.maximum(),posValue,sliderLength, self.width()

        # -- Done let sliders cross --
        if (self.active_slider>0) and (newPos < self._pos[self.active_slider-1]):
            newPos = self._pos[self.active_slider-1]+1
        if (self.active_slider<self._nsliders-1) and (newPos > self._pos[self.active_slider+1]):
            newPos = self._pos[self.active_slider+1]-1

        self.setValue(self.active_slider,newPos)
        #self.clickOffset = newPos
        self.update()
        self.sliderMoved.emit(*self._pos)



if __name__ == "__main__":
    import sys, signal
    def echo(handle,value):
        print '{0}: {1}'.format(handle,value)
    signal.signal(signal.SIGINT, signal.SIG_DFL) # Enable Ctrl-C
    app=QtGui.QApplication.instance() # checks if QApplication already exists 
    if not app: # create QApplication if it doesnt exist 
        app = QtGui.QApplication(sys.argv)
    '''
    '''
    slider = MultipleSlider(QtCore.Qt.Horizontal)
    slider.setMinimum(0)
    slider.setMaximum(100)
    slider.setTickPosition(QtGui.QSlider.TicksAbove)
    slider.sliderMoved.connect(echo)
    #app.setStyleSheet(mystyle)
    #slider = MultipleSlider()
    slider.show()
    app.exec_()

