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

def get_wcs_filename(fn):
    base = '.'.join(fn.split('.')[:-1])
    base = str(base)
    print 'Base filename', base
    wcsfn = base + '.wcs'
    return wcsfn

class HelloWorldApp(QWidget):
    ''' A Qt application that displays the text, "Hello, world!" '''
    def __init__(self, app):
        super(HelloWorldApp, self).__init__()
        self.app = app
        self.solveThreads = {}

        self.redraw_worker = None
        self.redraw_again = False
        
        # The image filename being solved/shown
        self.imagefn = None
        # The WCS filename
        self.wcsfn = None

        # The plotstuff plotting object
        self.plotstuff = None
        
        # Initialize the object as a QLabel
        self.statusLabel = QLabel('Hello, universe!')
        self.statusLabel.setAlignment(Qt.AlignCenter)

        #self.needsRedraw 
        
        openfile = QPushButton('Open Image', self)
        openfunc = Slot()(lambda: self.open_file())
        #openfile.clicked.connect(open_file)
        openfile.clicked.connect(openfunc)

        targetline = QHBoxLayout()
        targetline.addWidget(QLabel('Targets:'))
        tt = 'Planets, Polaris'
        self.targets = self.parse_targets(tt)
        self.targetBox = QLineEdit(tt, self)
        targetline.addWidget(self.targetBox)
        targetsfunc = Slot()(lambda: self.targets_changed())
        #self.targets.textEdited.connect(targetsfunc)
        self.targetBox.editingFinished.connect(targetsfunc)
        
        # A vertical box layout
        layout = QVBoxLayout()
        layout.addWidget(openfile)
        layout.addWidget(self.statusLabel)
        #layout.addWidget(targetline)
        layout.addItem(targetline)
        
        self.imagebox = DrawingPanel()

        # self.color = 'blue'
        # plot = Plotstuff('png', size=(W,H))
        # plot.color = 'blue'
        # plot.plot('fill')
        # img = plot.view_image_as_numpy()
        # print 'Image:', img.shape, img.dtype
        # #print img[:4,:4,:]
        # self.imagebox.setImage(img)
        #self.imagebox.setMinimumSize(QSize(H, H))
        layout.addWidget(self.imagebox, stretch=1)
        
        self.setLayout(layout)
        
        # Set the size, alignment, and title
        self.setMinimumSize(QSize(600, 600))
        self.setWindowTitle('Hello, universe!')
        #icon = QIcon('logo-128.png')
        icon = QIcon('gal-256.png')
        self.setWindowIcon(icon)

        fn = 'data/example.jpg'
        #self.imagefn = fn
        #self.solve_finished(fn)
        self.open_file(fn=fn)

    def replot_finished(self):
        print 'Redrawing plot finished.'
        self.redraw_worker = None
        if self.redraw_again:
            self.resizeEvent(None)
        self.update()
        
    def resizeEvent(self, event):
        print 'Resize'
        #self.redraw_plot()

        if self.redraw_worker is None:
            worker = RedrawPlotThread(self)
            finfunc = Slot(str)(lambda: self.replot_finished())
            worker.finishedSignal.connect(finfunc)
            self.redraw_again = False
            self.redraw_worker = worker
            print 'Starting redraw worker...'
            worker.start()
        else:
            self.redraw_again = True
            
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

    def parse_targets(self, targets):
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
        return targets
        
    def targets_changed(self):
        print 'targets changed:', self.targetBox.text()

        targets = self.parse_targets(self.targetBox.text())
        print 'Parsed targets:', targets
        if targets != self.targets:
            print 'Targets changed!'
            self.targets = targets
            self.redraw_plot()
            
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
        
    def open_file(self, fn=None):
        #if False: #True:
        #    fn = 'data/example.jpg'
        #else:
        if fn is None:
            fn,filt = QFileDialog.getOpenFileName(
                self, 'Open Image', os.path.join(os.getcwd(), 'data'),
                'Image Files (*.jpg)')
            fn = str(fn)
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

        wcsfn = get_wcs_filename(fn)
        if os.path.exists(wcsfn):
            print 'Using WCS header', wcsfn
            self.solve_finished(fn)
            return
        self.setStatus('Locating your image on the sky...')
        solve = SolveImageThread(fn)
        finfunc = Slot(str)(lambda fn: self.solve_finished(fn))
        solve.finishedSignal.connect(finfunc)
        print 'starting solve thread'
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
        wcsfn = get_wcs_filename(fn)
        if not os.path.exists(wcsfn):
            return
        print 'Solved!'
        self.wcsfn = wcsfn
        self.redraw_plot()

    def redraw_plot(self):
        wcsfn = self.wcsfn
        print 'wcsfn:', wcsfn, type(wcsfn)
        if wcsfn is None:
            self.setStatus('Failed to located your image on the sky!')
            return
        plot = self.make_plot()
        img = plot.view_image_as_numpy()
        print 'Image:', img.shape, img.dtype
        #print img[:4,:4,:]
        self.imagebox.setImage(img)

    def make_plot(self):
        w = self.imagebox.width()
        h = self.imagebox.height()
        wcs = Sip(self.wcsfn, 0)
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
    
        plot = Plotstuff('png', size=(w,h), ra=ra, dec=dec,
                         width=1.)
        plot.wcs_tan = plotwcs
        #print 'Plot WCS:'
        anwcs_print_stdout(plot.wcs)
        #print 'WCS:', str(plotwcs)
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
        plot.outline.wcs_file = self.wcsfn
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

        plot.bg_rgba = (0., 0., 0., 0.8)
        plot.bg_box = 1
        plot.pargs.marker_fg_layer = 1
        plot.apply_settings()
        jd = datetojd(self.imageTimestamp)
        for t in self.targets:
            if len(t) == 0:
                continue
            print 'Target: "%s"' % t
            if t in ['Jupiter', 'Mars']:
                ephem = InterpEphemeris('data/ephemerides/%s-ephem.fits' %
                                        t.lower())
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
        return plot
        
        
class InterpEphemeris(object):
    def __init__(self, filename):
        self.eph = fits_table(filename)
    def __call__(self, jd):
        # FIXME -- ugly!!
        ra  = np.interp(jd, self.eph.jd, self.eph.ra)
        dec = np.interp(jd, self.eph.jd, self.eph.dec)
        return ra,dec
        

class RedrawPlotThread(QThread):
    finishedSignal = Signal()

    def __init__(self, main):
        super(RedrawPlotThread, self).__init__()
        self.main = main

    def run(self):
        self.main.redraw_plot()
        self.finishedSignal.emit()
    
class SolveImageThread(QThread):
    finishedSignal = Signal(str)

    def __init__(self, fn):
        super(SolveImageThread, self).__init__()
        self.fn = fn

    def run(self):
        print 'Running'
        cmd = 'solve-field --continue --downsample 2 --objs 100 --no-plots %s' % self.fn
        os.system(cmd)
        #time.sleep(1)
        print 'Done!'
        self.finishedSignal.emit(self.fn)

print 'CWD:', os.getcwd()
print 'Exec:', os.path.dirname(sys.executable)

if getattr(sys, 'frozen', False):
    print 'Running in a PyInstaller bundle'
    basedir = sys._MEIPASS
else:
    print 'Running in a normal python environment'
    basedir = os.path.dirname(__file__)


# Create the QApplication object
app = QApplication(sys.argv)
# Create an instance of the application and run it
HelloWorldApp(app).run()
