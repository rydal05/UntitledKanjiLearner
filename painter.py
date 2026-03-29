from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import QMainWindow
from PySide6.QtSvg import * 

from PySide6.QtSvgWidgets import QSvgWidget

import os, time, sys, subprocess, random

from core.kanjivg_source import KanjiVGRepository, KanjiVGSourceError

kanjipath = "./kanji"

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

        self.pen_size = 8
        self.eraser_mode = False

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode #implement button toggle for eraser maybe idk

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
            if self.eraser_mode:
                pen.setWidth(max(1,int(self.pen_size*self.pen_pressure)))
                pen.setColor(QColor('white'))
            else:
                pen.setWidth(max(1,int(self.pen_size*self.pen_pressure)))
                pen.setColor(QColor('black'))

            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)    
            painter.setPen(pen)
            painter.drawLine(from_point, to_point)
        self.label.setPixmap(pixmap)
        self.update()
    
    def keyPressEvent(self, event):
        key = event.key()

        if(key == Qt.Key_E):
            self.toggle_eraser()
        elif(key == Qt.Key_R):
            path = self.select_random()
            self.load_svg(path)

            print(f"{path}")
            print("made it through")

            
        super().keyPressEvent(event)
    
    def select_random(self):
        entries = os.listdir(kanjipath)

        files = [f for f in entries if os.path.isfile(os.path.join(kanjipath, f))]

        if not files:
            return "COULDN'T LOCATE KANJI SVGs"

        random_filename = random.choice(files)

        return os.path.join(kanjipath, random_filename)

    def load_svg(self,path):
        renderer = QSvgRenderer(path)
        
        pixmap = QPixmap(self.label.size())
        pixmap.fill(Qt.white)
        with QPainter(pixmap) as painter:
            renderer.render(painter)
        self.label.setPixmap(pixmap)
        self.label.update()


app=QtWidgets.QApplication(sys.argv)

try:
    kanjipath = str(KanjiVGRepository().ensure_ready("main"))
except KanjiVGSourceError as exc:
    # Keep local development behavior if network or API access fails.
    print(f"KanjiVG cache setup failed, using local path {kanjipath}: {exc}")

window=MainWindow()
window.show()
app.exec()