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
        self.resize(640,480)
        self.label.setScaledContents(True)
        canvas.fill(Qt.white)
        self.label.setPixmap(canvas)


        self.setCentralWidget(self.label)

        self.setAttribute(Qt.WA_AcceptTouchEvents, False)


    def resizeEvent(self, event):
        old_pixmap = self.label.pixmap()
        scaled = old_pixmap.scaled(
            self.label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.label.setPixmap(scaled)
        super().resizeEvent(event)

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

app=QtWidgets.QApplication(sys.argv)
window=MainWindow()
window.show()
app.exec()