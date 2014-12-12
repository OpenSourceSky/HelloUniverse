import sys
 
# Import the core and GUI elements of Qt
from PySide.QtCore import *
from PySide.QtGui import *

import numpy as np

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
        
    def setImage(self, image, format=QImage.Format_ARGB32):
        ''' numpy image '''
        H,W,planes = image.shape
        #self.npimage = image.copy()
        #print self.npimage[:4,:4,:]
        #print 'NP image:', self.npimage
        #self.qimage = QImage(self.npimage.data, W, H, format)
        #self.qimage = QImage(self.npimage.tobytes(), W, H, format)
        #self.qimage = QImage(self.npimage, W, H, format)

        #a = self.npimage
        #B = (255 << 24) | (a[:,:,1] << 16) | (a[:,:,2] << 8) | (a[:,:,3])
        #self.qimage = QImage(B.flatten(), W, H, QImage.Format_RGB32)        

        #a = self.npimage
        #B = np.frombuffer(a.data, dtype=np.uint32, #B = (255 << 24) | (a[:,:,1] << 16) | (a[:,:,2] << 8) | (a[:,:,3])
        self.qimage = QImage(
            # (image[:,:,0].astype(np.uint32) << 24) | 
            # (image[:,:,1].astype(np.uint32) << 16) | 
            # (image[:,:,2].astype(np.uint32) << 8 ) | 
            # (image[:,:,3].astype(np.uint32)),
            (image[:,:,0] * (1<<24)) |
            (image[:,:,1] * (1<<16)) |
            (image[:,:,2] * (1<<8)) |
            (image[:,:,3]),
            W, H, QImage.Format_RGB32)        
        
        #a = np.random.randint(0,256,size=(100,100,3)).astype(np.uint32)
        #B = (255 << 24) | (a[:,:,0] << 16) | (a[:,:,1] << 8) | (a[:,:,2])
        #self.qimage = QImage(B.flatten(), W, H, QImage.Format_RGB32)        

        #print 'bytes:', self.npimage.tobytes()
        #print 'bytes:', repr(self.npimage.tobytes())
        
    def paintEvent(self, event):
        p = QPainter(self)
        print 'size', self.size()
        if self.qimage is not None:
            print 'Drawing image'
            #p.drawImage(0, 0, self.qimage)
            rect = QRect(QPoint(0,0), self.size())
            print 'rect:', rect
            print 'image size:', self.qimage.size()
            sourcerect = QRect(QPoint(0,0), self.qimage.size())
            #p.drawImage(rect, self.qimage, sourcerect)
            p.drawImage(rect, self.qimage)
            
#class HelloWorldApp(QLabel):
class HelloWorldApp(QWidget):
    ''' A Qt application that displays the text, "Hello, world!" '''
    def __init__(self):
        super(HelloWorldApp, self).__init__()
        # Initialize the object as a QLabel
        #win = QWidget()
        label = QLabel('Hello, world!')
        label.setAlignment(Qt.AlignCenter)

        # A vertical box layout
        layout = QVBoxLayout()
        layout.addWidget(label)

        imagebox = CustomWidget()
        W,H = 5,5
        img = np.zeros((H,W, 4), np.uint8)
        img[:,:,0] = 255
        img[:,:,1] = np.linspace(0, 255, H).astype(np.uint8)[:,np.newaxis]
        img[:,:,2] = np.linspace(0, 255, W).astype(np.uint8)[np.newaxis,:]
        imagebox.setImage(img)
        imagebox.setMinimumSize(QSize(400, 400))
        layout.addWidget(imagebox)
        
        self.setLayout(layout)
        
        # Set the size, alignment, and title
        self.setMinimumSize(QSize(600, 400))
        self.setWindowTitle('Hello, world!')
 
    def run(self, qt_app):
        ''' Show the application window and start the main event loop '''
        #self.showFullScreen()
        self.show()
        self.raise_()
        qt_app.exec_()

    def keyPressEvent(self, event):
        super(HelloWorldApp, self).keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            # if self.isFullScreen():
            #     self.showNormal()
            #     self.showMaximized()
            # else:
            #     self.showFullScreen()
            self.close()
        
# Create the QApplication object
qt_app = QApplication(sys.argv)
# Create an instance of the application and run it
HelloWorldApp().run(qt_app)
