import sys

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout, QHBoxLayout, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *


def foo():
    print('dsfsafsda')

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AutoGear")
        self.setWindowIcon(QIcon('ico.png'))

        # setting  the geometry of window
        self.resize(1000, 1000)

        # creating a label widget and setting properties
        self.label_1 = QLabel("Bottom", self)
        self.label_1.move(20, 100)
        self.label_1.resize(60, 60)
        self.label_1.setStyleSheet("border: 1px solid black;")
 
        # aligning label to the bottom
        self.label_1.setAlignment(Qt.AlignBottom)
 
        # creating a label widget and setting properties
        self.label_2 = QLabel("Center", self)
        self.label_2.move(90, 100)
        self.label_2.resize(60, 60)
        self.label_2.setStyleSheet("border: 1px solid black;")
 
        # aligning label to the center
        self.label_2.setAlignment(Qt.AlignCenter)
 
        # creating a label widget and setting properties
        self.label_3 = QLabel("Left", self)
        self.label_3.move(160, 100)
        self.label_3.resize(60, 60)
        self.label_3.setStyleSheet("border: 1px solid black;")
 
        # aligning label to the left
        self.label_3.setAlignment(Qt.AlignLeft)
 
        # creating a label widget and setting properties
        self.label_4 = QLabel("Right", self)
        self.label_4.move(230, 100)
        self.label_4.resize(60, 60)
        self.label_4.setStyleSheet("border: 1px solid black;")
 
        # aligning label to the right
        self.label_4.setAlignment(Qt.AlignRight)
 
        # creating a label widget and setting properties
        self.label_5 = QLabel("Top", self)
        self.label_5.move(300, 100)
        self.label_5.resize(60, 60)
        self.label_5.setStyleSheet("border: 1px solid black;")
 
        # aligning label to the top
        self.label_5.setAlignment(Qt.AlignTop)
 
        # creating a label widget and setting properties
        self.label_6 = QLabel("H center", self)
        self.label_6.move(370, 100)
        self.label_6.resize(60, 60)
        self.label_6.setStyleSheet("border: 1px solid black;")
 
        # aligning label to the Hcenter
        self.label_6.setAlignment(Qt.AlignHCenter)
 
        # creating a label widget and setting properties
        self.label_7 = QLabel("V center", self)
        self.label_7.move(440, 100)
        self.label_7.resize(60, 60)
        self.label_7.setStyleSheet("border: 1px solid black;")
 
        # aligning label to the Vcenter
        self.label_7.setAlignment(Qt.AlignVCenter)

        btn = QPushButton(self)
        btn.setText('Start')
        btn.show()
        btn.clicked.connect(foo)

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)

        hbox.setAlignment(Qt.AlignCenter)
        hbox.addStretch()

        hbox.addWidget(btn)
        hbox.addStretch() 
        vbox.addLayout(hbox)
        vbox.setAlignment(Qt.AlignCenter)
 
        # show all the widgets
        self.show()


def window():
    app = QApplication(sys.argv)
    w = QWidget()
    b = QLabel(w)

    w.resize(1000, 1000)
    w.setWindowTitle("AutoGear")
    w.setWindowIcon(QIcon('ico.png'))


    btn = QPushButton(w)
    btn.setText('Start')
    btn.show()
    btn.clicked.connect(foo)

    vbox = QVBoxLayout()
    hbox = QHBoxLayout()
    hbox.setContentsMargins(0, 0, 0, 0)

    hbox.setAlignment(Qt.AlignCenter)
    hbox.addStretch()

    hbox.addWidget(btn)
    hbox.addStretch() 
    vbox.addLayout(hbox)
    vbox.setAlignment(Qt.AlignCenter)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
     
    # create pyqt5 app
    App = QApplication(sys.argv)
    
    # create the instance of our Window
    window = Window()
    
    # start the app
    sys.exit(App.exec())