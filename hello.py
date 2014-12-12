import sys
 
# Import the core and GUI elements of Qt
from PySide.QtCore import *
from PySide.QtGui import *

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

class HelloWorldApp(QLabel):
    ''' A Qt application that displays the text, "Hello, world!" '''
    def __init__(self):
        # Initialize the object as a QLabel
        QLabel.__init__(self, "Hello, world!")
 
        # Set the size, alignment, and title
        self.setMinimumSize(QSize(600, 400))
        self.setAlignment(Qt.AlignCenter)
        self.setWindowTitle('Hello, world!')
 
    def run(self, qt_app):
        ''' Show the application window and start the main event loop '''
        #self.showFullScreen()
        self.show()
        #self.activateWindow()
        self.raise_()
        #print dir(self)
        print 'pre .exec()'
        qt_app.exec_()
        print 'post .exec()'

    '''
    def keyPressEvent(self, event):
        QtGui.QLabel.keyPressEvent(self, event)
        if event.key() == QtCore.Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
                self.showMaximized()
            else:
                self.showFullScreen()
    '''

        
# Create the QApplication object
qt_app = QApplication(sys.argv)
# Create an instance of the application and run it
HelloWorldApp().run(qt_app)
