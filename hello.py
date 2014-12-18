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
from astrometry.util.fits import *
from astrometry.util import EXIF
from astrometry.util.starutil_numpy import *

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

class DrawingPanel(QWidget):
    def __init__(self):
        super(DrawingPanel, self).__init__()
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

            # (image[:,:,3] * (1<<24)) |
            # (image[:,:,0] * (1<<16)) |
            # (image[:,:,1] * (1<<8)) |
            # (image[:,:,2]),

            (image[:,:,3] * (1<<24)) |
            (image[:,:,2] * (1<<16)) |
            (image[:,:,1] * (1<<8)) |
            (image[:,:,0]),
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
        self.statusLabel = QLabel('Hello, universe!')
        self.statusLabel.setAlignment(Qt.AlignCenter)

        openfile = QPushButton('Open Image', self)
        openfunc = Slot()(lambda: self.open_file())
        #openfile.clicked.connect(open_file)
        openfile.clicked.connect(openfunc)

        targetline = QHBoxLayout()
        targetline.addWidget(QLabel('Targets:'))
        self.targets = QLineEdit('Planets, Polaris', self)
        targetline.addWidget(self.targets)
        targetsfunc = Slot()(lambda: self.targets_changed())
        #self.targets.textEdited.connect(targetsfunc)
        self.targets.editingFinished.connect(targetsfunc)
        
        # A vertical box layout
        layout = QVBoxLayout()
        layout.addWidget(openfile)
        layout.addWidget(self.statusLabel)
        #layout.addWidget(targetline)
        layout.addItem(targetline)
        
        self.imagebox = DrawingPanel()
        W,H = 600,400

        self.color = 'blue'
        plot = Plotstuff('png', size=(W,H))
        plot.color = 'blue'
        plot.plot('fill')
        img = plot.view_image_as_numpy()
        print 'Image:', img.shape, img.dtype
        #print img[:4,:4,:]
        
        self.imagebox.setImage(img)
        self.imagebox.setMinimumSize(QSize(400, 400))
        layout.addWidget(self.imagebox)
        
        self.setLayout(layout)
        
        # Set the size, alignment, and title
        self.setMinimumSize(QSize(600, 400))
        self.setWindowTitle('Hello, universe!')
        icon = QIcon('logo-128.png')
        self.setWindowIcon(icon)
 
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

    def targets_changed(self):
        print 'targets changed:', self.targets.text()

        # ncolor = dict(blue='green', green='red', red='blue')
        # self.color = ncolor[self.color]
        # print 'color', self.color
        # 
        # W,H = self.size().width(), self.size().height()
        # plot = Plotstuff('png', size=(W,H))
        # plot.color = self.color
        # plot.plot('fill')
        # img = plot.view_image_as_numpy()
        # print 'Image:', img.shape, img.dtype
        # print img[:4,:4,:]
        # self.imagebox.setImage(img)
        self.redraw_plot()
        
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

        self.imageTimestamp = timestamp

        self.setStatus('Locating your image on the sky...')
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
        self.setStatus('Located your image on the sky!')
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
        self.redraw_plot()


    def redraw_plot(self):
        wcsfn = self.wcsfn
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
        plot.alpha = 0.5
        plot.plot_grid(10., 10., 10., 10.)

        plot.ann.constellations = True
        plot.ann.constellation_lines = True
        plot.ann.constellation_labels = True
        plot.ann.constellation_pastel = True
        plot.ann.bright = False
        plot.plot('annotations')

        
        targets = self.targets.text()
        # split by ' ' or ','
        # targets = targets.strip().split(' ')
        # tt = []
        # for t in targets:
        #     tt.extend(t.split(','))
        # targets = tt
        targets = targets.strip().split(',')
        targets = [t.strip() for t in targets]
        
        # Expand aliases
        aliases = dict(planets=['Mercury','Venus','Mars','Jupiter','Saturn',
                                'Neptune','Uranus'])
        tt = []
        for t in targets:
            tt.extend(aliases.get(t.lower(), [t]))
        targets = tt
        print 'Targets:', targets
            
        plot.bg_rgba = (0., 0., 0., 0.8)
        plot.bg_box = 1
        plot.pargs.marker_fg_layer = 1
        plot.apply_settings()
        jd = datetojd(self.imageTimestamp)
        for t in targets:
            if len(t) == 0:
                continue
            print 'Target: "%s"' % t
            if t in ['Jupiter', 'Mars']:
                ephem = InterpEphemeris('%s-ephem.fits' % t.lower())
                ra,dec = ephem(jd)
                plot.ann.add_target(ra, dec, t)
            else:
                plot.ann.add_named_target(str(t))
                
        plot.color = 'green'
        plot.ann.constellations = False
        plot.ann.constellation_lines = False
        plot.ann.constellation_labels = False
        plot.ann_constellation_pastel = False
        plot.plot('annotations')
                
        img = plot.view_image_as_numpy()
        print 'Image:', img.shape, img.dtype
        #print img[:4,:4,:]
        self.imagebox.setImage(img)
        
        
class InterpEphemeris(object):
    def __init__(self, filename):
        self.eph = fits_table(filename)
    def __call__(self, jd):
        # FIXME -- ugly!!
        ra  = np.interp(jd, self.eph.jd, self.eph.ra)
        dec = np.interp(jd, self.eph.jd, self.eph.dec)
        return ra,dec
        

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
