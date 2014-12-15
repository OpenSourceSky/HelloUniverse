import sys
import os
import time
import datetime

# Import the core and GUI elements of Qt
from PySide.QtCore import *
from PySide.QtGui import *

import numpy as np

from astrometry.blind.plotstuff import *
from astrometry.util.util import *
from astrometry.util import EXIF

'''

widget.setMinimumSize(QSize(800, 600))
widget.setMinimumSize(QSize(800, 600))
label = QLabel('Hello, world!', parent_widget)
label.setAlignment(Qt.AlignCenter)
QLabel.setWordWrap(True);

QPushButton(parent=None)
QPushButton(text, [parent=None])
QPushButton(icon, text, [parent=None])

pixmap = QtGui.QPixmap('hoge.jpg')
screen = QtGui.QLabel()
screen.setPixmap(pixmap)
screen.show()
screen.showFullScreen()
sys.exit(app.exec_())



'''

class CustomWidget(QWidget):
    def __init__(self):
        super(CustomWidget, self).__init__()
        self.qimage = None

    def setQImage(self, qim):
        self.qimage = qim
        self.repaint()
        
    def setImage(self, image, format=QImage.Format_ARGB32):
        ''' numpy image '''
        H,W,planes = image.shape
        self.setQImage(QImage(
            # (image[:,:,0] * (1<<24)) |
            # (image[:,:,1] * (1<<16)) |
            # (image[:,:,2] * (1<<8)) |
            # (image[:,:,3]),
            (image[:,:,3] * (1<<24)) |
            (image[:,:,0] * (1<<16)) |
            (image[:,:,1] * (1<<8)) |
            (image[:,:,2]),
            W, H, QImage.Format_RGB32))
        
    def paintEvent(self, event):
        p = QPainter(self)
        if self.qimage is not None:
            #p.drawImage(0, 0, self.qimage)
            rect = QRect(QPoint(0,0), self.size())
            p.drawImage(rect, self.qimage)

class HelloWorldApp(QWidget):
    ''' A Qt application that displays the text, "Hello, world!" '''
    def __init__(self, app):
        super(HelloWorldApp, self).__init__()
        self.app = app
        self.solveThreads = {}

        # The image filename being solved/shown
        self.imagefn = None
        # The WCS filename
        self.wcsfn = None

        # The plotstuff plotting object
        self.plotstuff = None
        
        # Initialize the object as a QLabel
        self.statusLabel = QLabel('Hello, world!')
        self.statusLabel.setAlignment(Qt.AlignCenter)

        openfile = QPushButton('Open Image', self)
        openfunc = Slot()(lambda: self.open_file())
        #openfile.clicked.connect(open_file)
        openfile.clicked.connect(openfunc)

        # A vertical box layout
        layout = QVBoxLayout()
        layout.addWidget(openfile)
        layout.addWidget(self.statusLabel)

        self.imagebox = CustomWidget()
        W,H = 600,400

        plot = Plotstuff('png', size=(W,H))
        plot.color = 'blue'
        plot.plot('fill')
        img = plot.view_image_as_numpy()
        print 'Image:', img.shape, img.dtype
        print img[:4,:4,:]
        
        self.imagebox.setImage(img)
        self.imagebox.setMinimumSize(QSize(400, 400))
        layout.addWidget(self.imagebox)
        
        self.setLayout(layout)
        
        # Set the size, alignment, and title
        self.setMinimumSize(QSize(600, 400))
        self.setWindowTitle('Hello, world!')
 
    def run(self):
        ''' Show the application window and start the main event loop.

        DOES NOT RETURN until the gui is closed.
        '''
        #self.showFullScreen()
        self.show()
        self.raise_()
        self.app.exec_()

    def keyPressEvent(self, event):
        super(HelloWorldApp, self).keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            # if self.isFullScreen():
            #     self.showNormal()
            #     self.showMaximized()
            # else:
            #     self.showFullScreen()
            self.close()

    def setStatus(self, txt):
        self.statusLabel.setText(txt)
            
    def open_file(self):
        print 'open_file'

        if True:
            fn = '/Users/dstn/qt/photos/IMG_9346.JPG'
        else:
            fn,filt = QFileDialog.getOpenFileName(
                self, 'Open Image', os.getcwd(),
                'Image Files (*.jpg)')
        print 'selected file:', fn
        if fn == '':
            return

        self.imagefn = fn
        
        qim = QImage(fn)
        if qim == None:
            return
        self.imagebox.setQImage(qim)

        f = open(fn, 'rb')
        exif = EXIF.process_file(f)
        #print 'exif:', exif
        for k in exif.keys():
            print 'EXIF key:', k
            try:
                print str(exif[k])
            except:
                pass

        timestamp = None
        try:
            datestr = exif.get('EXIF DateTimeOriginal')
            if not datestr:
                datestr = exif.get('Image DateTime')
            if datestr:
                timestamp = datetime.datetime.strptime(str(datestr),
                                                       '%Y:%m:%d %H:%M:%S')
                print 'Timestamp:', timestamp
        except:
            import traceback
            traceback.print_exc()
            pass
        if timestamp is None:
            timestamp = datetime.datetime.now()
        
        print 'creating solve thread'
        solve = SolveImageThread(fn)
        print 'defining finished function'
        finfunc = Slot(str)(lambda fn: self.solve_finished(fn))
        print finfunc
        print 'connecting'
        solve.finishedSignal.connect(finfunc)
        print 'starting thread'
        solve.start()
        # FIXME -- if it already existed?
        self.solveThreads[fn] = solve
        
    def solve_finished(self, fn):
        print 'Solve finished:', fn
        try:
            del self.solveThreads[fn]
        except:
            pass
        base = '.'.join(fn.split('.')[:-1])
        base = str(base)
        print 'Base filename', base
        wcsfn = base + '.wcs'
        if not os.path.exists(wcsfn):
            return
        print 'Solved!'
        self.wcsfn = wcsfn

        print 'wcsfn:', wcsfn, type(wcsfn)
        wcs = Sip(wcsfn, 0)
        w = self.imagebox.width()
        h = self.imagebox.height()
        ra,dec = wcs.radec_center()
        print 'RA,Dec center', ra,dec
        pixscale = wcs.pixel_scale()
        imw = wcs.get_width()
        imh = wcs.get_height()
        scale = 2. / min(w / float(imw), h / float(imh))

        plotwcs = Tan(ra, dec, w/2.+0.5, h/2.+0.5,
                      wcs.cd[0]*scale, wcs.cd[1]*scale,
                      wcs.cd[2]*scale, wcs.cd[3]*scale,
                      w, h)
        
        self.plotstuff = Plotstuff('png', size=(w,h), ra=ra, dec=dec,
                                   width=1.)
        plot = self.plotstuff
        plot.wcs_tan = plotwcs
        print 'Plot WCS:'
        anwcs_print_stdout(plot.wcs)
        print 'WCS:', str(plotwcs)
        plot.color = 'black'
        plot.alpha = 1.
        plot.apply_settings()
        plot.plot('fill')

        plot.color = 'white'
        plot.resample = 1
        plot.apply_settings()
        plot.image.set_file(self.imagefn)
        plot.image.set_wcs_file(self.wcsfn, 0)
        plot.plot('image')

        plot.color = 'green'
        plot.outline.wcs_file = wcsfn
        plot.plot('outline')

        plot.color = 'gray'
        plot.plot_grid(10., 10., 10., 10.)
        img = plot.view_image_as_numpy()
        print 'Image:', img.shape, img.dtype
        print img[:4,:4,:]
        self.imagebox.setImage(img)
        
class SolveImageThread(QThread):
    finishedSignal = Signal(str)

    def __init__(self, fn):
        super(SolveImageThread, self).__init__()
        self.fn = fn

    def run(self):
        print 'Running'
        cmd = 'solve-field --continue --downsample 2 --objs 100 --no-plots %s' % self.fn
        #os.system(cmd)
        time.sleep(1)
        print 'Done!'
        self.finishedSignal.emit(self.fn)
        
# Create the QApplication object
app = QApplication(sys.argv)
# Create an instance of the application and run it
HelloWorldApp(app).run()
