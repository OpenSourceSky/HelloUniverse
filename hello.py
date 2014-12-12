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
        self.qimage = QImage(
            (image[:,:,0] * (1<<24)) |
            (image[:,:,1] * (1<<16)) |
            (image[:,:,2] * (1<<8)) |
            (image[:,:,3]),
            W, H, QImage.Format_RGB32)        
        
    def paintEvent(self, event):
        p = QPainter(self)
        if self.qimage is not None:
            #p.drawImage(0, 0, self.qimage)
            rect = QRect(QPoint(0,0), self.size())
            p.drawImage(rect, self.qimage)

class HelloWorldApp(QWidget):
    ''' A Qt application that displays the text, "Hello, world!" '''
    def __init__(self):
        super(HelloWorldApp, self).__init__()
        # Initialize the object as a QLabel
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
