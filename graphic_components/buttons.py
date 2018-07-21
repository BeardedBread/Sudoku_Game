"""This module contains all the buttons used. A base class AnimBox handles the drawing and animation, inherited
by all the buttons.
"""

import math

from PyQt5.QtCore import (QAbstractAnimation, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal)
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import (QGraphicsObject)

from .textbox import AnimatedText


class AnimBox(QGraphicsObject):
    # Prepare the signal
    hoverEnter = pyqtSignal()
    hoverExit = pyqtSignal()

    # Initialisation
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(parent=parent)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.circumference = 2*(width+height)

        # Set up pens for drawing
        self.default_pen = QPen()
        self.default_pen.setColor(Qt.white)
        self.outline_pen = QPen()
        self.outline_pen.setColor(Qt.white)
        self.outline_pen.setWidth(5)

        # Whether the mouse hover over the box
        self.detected = False
        self.btn_rect = QRectF(self.x, self.y, self.width, self.height)
        # The 4 lines to construct the box
        self.left = QLineF()
        self.down = QLineF()
        self.right = QLineF()
        self.up = QLineF()

        self.line_order = [self.up, self.right, self.down, self.left]

        self.set_freeze(False)

        # Length of the box to be drawn
        self.length = 0
        # Set up the length to be animated
        self.anim = QPropertyAnimation(self, b'length')
        self.anim.setStartValue(0)
        for t in range(1, 10):
            self.anim.setKeyValueAt(t / 10, self.logistic_func(t / 10))
        self.anim.setEndValue(self.circumference)

    def set_freeze(self, freeze):
        if freeze:
            self.setAcceptedMouseButtons(Qt.NoButton)
            self.setAcceptHoverEvents(False)
        else:
            self.setAcceptedMouseButtons(Qt.LeftButton)
            self.setAcceptHoverEvents(True)

    # Toggle the animation to be play forward or backward
    def toggle_anim(self, toggling):
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    # The logistic function that determines the animation motion
    def logistic_func(self, x):
        return self.circumference / (1+math.exp(-(x-0.5)*18))

    # Reimplemented boundingRect
    def boundingRect(self):
        return QRectF(self.x-5, self.y-5, self.width+10, self.height+10)

    # Reimplemented paint
    def paint(self, painter, style, widget=None):
        painter.setPen(self.outline_pen)
        for line in self.line_order:
            if line.length() > 1:
                painter.drawLine(line)
        painter.setPen(self.default_pen)
        painter.drawRect(self.btn_rect)

    # Defining the length to be drawn as a pyqtProperty
    @pyqtProperty(float)
    def length(self):
        return self._length

    # Determine the length of the four lines to be drawn
    @length.setter
    def length(self, value):
        self._length = value
        remaining_length = value
        if remaining_length >= 2 * self.width + self.height:
            length_to_draw = remaining_length - (2 * self.width + self.height)
            remaining_length -= length_to_draw
        else:
            length_to_draw = 0

        self.line_order[3].setLine(self.x, self.y + self.height,
                                   self.x, self.y + self.height - length_to_draw)
        if remaining_length >= self.width + self.height:
            length_to_draw = remaining_length - (self.width + self.height)
            remaining_length -= length_to_draw
        else:
            length_to_draw = 0
        self.line_order[2].setLine(self.x + self.width, self.y + self.height,
                                   self.x + self.width - length_to_draw,
                                   self.y + self.height)

        if remaining_length >= self.width:
            length_to_draw = remaining_length - self.width
            remaining_length -= length_to_draw
        else:
            length_to_draw = 0

        self.line_order[1].setLine(self.x + self.width, self.y,
                                   self.x + self.width, self.y + length_to_draw)
        self.line_order[0].setLine(self.x, self.y,
                                   self.x + remaining_length, self.y)
        self.update()

    # Reimplemented hoverEvents to detect the mouse and toggle the animation
    def hoverEnterEvent(self, event):
        if ~self.detected:
            self.hoverEnter.emit()
            self.detected = True
            self.toggle_anim(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if self.detected:
            self.hoverExit.emit()
            self.detected = False
            self.toggle_anim(False)
        super().hoverLeaveEvent(event)


class RingButton(AnimBox):
    # Prepare the signal
    buttonClicked = pyqtSignal(str)

    # Initialisation
    def __init__(self, x, y, width, height, text, parent=None):
        super().__init__(x, y, width, height, parent=parent)
        self.text = text
        self.transparent = False

    def set_transparent(self, state):
        self.transparent = state
        col = self.default_pen.color()
        if state:
            col.setAlphaF(0.2)
        else:
            col.setAlphaF(1)
        self.default_pen.setColor(col)
        self.update()

    # Reimplemented paint
    def paint(self, painter, style, widget=None):
        super().paint(painter, style, widget)
        painter.setPen(self.default_pen)
        if self.transparent:
            painter.fillRect(self.btn_rect, QColor(255, 255, 255, 0.1))
        else:
            painter.fillRect(self.btn_rect, Qt.black)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)

    def mousePressEvent(self, event):
        self.toggle_anim(False)
        self.buttonClicked.emit(self.text)


class MenuButton(AnimBox):
    # Prepare the signal
    buttonClicked = pyqtSignal(str)

    # Initialisation
    def __init__(self, x, y, width, height, text, parent=None):
        super().__init__(x, y, width, height, parent=parent)
        self.text = text
        self.animText = AnimatedText(text, parent=self)

    def paint(self, painter, style, widget=None):
        super().paint(painter, style, widget)
        painter.fillRect(self.btn_rect, Qt.black)

    def mousePressEvent(self, event):
        self.toggle_anim(False)
        self.buttonClicked.emit(self.text)



