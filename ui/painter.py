from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

import os, time, sys, subprocess
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.pen_pressure = 1
        self.last_point = None
        self.is_drawing = False

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(640,480)
        canvas.fill(Qt.white)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

        self.setAttribute(Qt.WA_AcceptTouchEvents, False)

    def tabletEvent(self, event):
        event_type = event.type()

        print(f"{event_type}")

        print(f"{QEvent.Type.TabletPress}")
        print(f"{QEvent.Type.TabletMove}")
        print(f"{QEvent.Type.TabletRelease}")


        if(event_type == QEvent.Type.TabletPress):
            self.is_drawing = True
            self.last_point = event.position()
        elif(event_type == QEvent.Type.TabletMove):
            if(self.is_drawing):
                self.pen_pressure = event.pressure()
                self._draw_line(self.last_point, event.position())
                self.last_point = event.position()
                
        elif(event_type == QEvent.Type.TabletRelease):
            self.is_drawing = False
            self.last_point = None

        event.accept()


    def _draw_line(self, from_point, to_point):
        pixmap = self.label.pixmap()
        with QPainter(pixmap) as painter:
            pen = QPen()
            pen.setWidth(max(1,int(8*self.pen_pressure)))
            pen.setColor(QColor('black'))
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(from_point, to_point)
        self.label.setPixmap(pixmap)
        self.update()
        
    # def mouseMoveEvent(self,event):
    #     if self.last_point is None:
    #         self.last_point = event.position()
    #         return
        
    #     with QPainter(self.label.pixmap()) as painter:
    #         pen = painter.pen()
    #         painter.setPen(pen)
    #         self._draw_line(self.last_point, event.position())
            
    #     self.update()

    #     self.last_point = event.position()

    # def mouseReleaseEvent(self, event):
    #     self.last_point = None

    # def drawpoint(self):
    #     with QPainter(self.label.pixmap()) as painter:
    #         painter.drawPoint(200,150)
            
    # def drawSquare(self):
    #     with QPainter(self.label.pixmap()) as painter:
    #         pen = QtGui.QPen()
    #         pen.setWidth(40)
    #         pen.setColor(QtGui.QColor('red'))
    #         painter.setPen(pen)
    #         painter.drawPoint(200,150)
            
    # def drawRandom(self):
    #     from random import randint, choice
    #     colors = ['#FFD141', '#376F9F', '#0D1F2D', '#E9EBEF', '#EB5160']

    #     with QPainter(self.label.pixmap()) as painter: #required to open drawing process
        
    #         pen = QtGui.QPen() # required to give painter unique attributes (size, color, etc)
    #         pen.setWidth(3)
            
    #         painter.setPen(pen) # required for dynaimc updating of pen characteristics

    #         for n in range(10000):
    #             pen.setColor(QtGui.QColor(choice(colors)))
    #             painter.setPen(pen) # update pen
    #             painter.drawPoint(
    #                 200+randint(-100,100),
    #                 150+randint(-100,100)
    #             )
    #         #required to end drawing operation like SQL


app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec()