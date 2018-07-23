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
    """A Box that draws an outline when hover over.

    Attributes
    ----------
    hoverEnter: pyqtSignal
        Emitted when the mouse hover into the box
    hoverExit: pyqtSignal
        Emitted when the mouse hover out of the box
    """
    hoverEnter = pyqtSignal()
    hoverExit = pyqtSignal()

    def __init__(self, x, y, width, height, parent=None):
        """Prepares the box and animation

        Parameters
        ----------
        x: float
            x position of the top-left corner of the box
        y: float
            y position of the top-left corner of the box
        width: float
            Width of the box
        height: float
            Height of the box
        parent: object
            Passed into QGraphicsObject init method
        """
        super().__init__(parent=parent)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.circumference = 2*(width+height)

        self.default_pen = QPen()
        self.default_pen.setColor(Qt.white)
        self.outline_pen = QPen()
        self.outline_pen.setColor(Qt.white)
        self.outline_pen.setWidth(5)

        self.detected = False  # Whether the mouse hover over the box
        self.btn_rect = QRectF(self.x, self.y, self.width, self.height)

        self.left = QLineF()
        self.down = QLineF()
        self.right = QLineF()
        self.up = QLineF()

        self.line_order = [self.up, self.right, self.down, self.left]

        self.set_freeze(False)

        self.length = 0
        self.anim = QPropertyAnimation(self, b'length')
        self.anim.setStartValue(0)
        for t in range(1, 10):
            self.anim.setKeyValueAt(t / 10, self.logistic_func(t / 10))
        self.anim.setEndValue(self.circumference)

    def set_freeze(self, freeze):
        """Set whether the box should accept the mouse events

        Parameters
        ----------
        freeze: bool
            True to stop the box from accepting mouse inputs, False otherwise
        """
        if freeze:
            self.setAcceptedMouseButtons(Qt.NoButton)
            self.setAcceptHoverEvents(False)
        else:
            self.setAcceptedMouseButtons(Qt.LeftButton)
            self.setAcceptHoverEvents(True)

    def toggle_anim(self, toggling):
        """Toggle the highlight animation to be play forward or backward

        Parameters
        ----------
        toggling: bool
            True for forward, False for backwards
        """
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    def logistic_func(self, x):
        """The logistic function that determines the animation motion

        Parameters
        ----------
        x: list or numpy array
            Values to be feed into the function

        Returns
        -------
        list or numpy array
            Values of the logistic function corresponding to the input range

        """
        return self.circumference / (1+math.exp(-(x-0.5)*18))

    def boundingRect(self):
        """Reimplemented from QGraphicsObject.
        """
        return QRectF(self.x-5, self.y-5, self.width+10, self.height+10)

    def paint(self, painter, style, widget=None):
        """Reimplemented from QGraphicsObject. Draws the Box and the highlights.
        """
        painter.setPen(self.outline_pen)
        for line in self.line_order:
            if line.length() > 1:
                painter.drawLine(line)
        painter.setPen(self.default_pen)
        painter.drawRect(self.btn_rect)

    @pyqtProperty(float)
    def length(self):
        """float: The length of the highlight to be drawn.
        When set, the length of the outlines are determined
        """
        return self._length

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

    def hoverEnterEvent(self, event):
        """Reimplemented hoverEnterEvent. Detect the mouse and toggle the animation
        """
        if ~self.detected:
            self.hoverEnter.emit()
            self.detected = True
            self.toggle_anim(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        """Reimplemented hoverLeaveEvent. Detect the mouse leaving and reverse the animation
        """
        if self.detected:
            self.hoverExit.emit()
            self.detected = False
            self.toggle_anim(False)
        super().hoverLeaveEvent(event)


class RingButton(AnimBox):
    """Button specific to the Number Ring. Contains the function to be transparent

    Attributes
    ----------
    buttonClicked: pyqtSignal(str)
        Emitted when it is clicked. Sends the text of the button
    """
    buttonClicked = pyqtSignal(str)

    # Initialisation
    def __init__(self, x, y, width, height, text, parent=None):
        """Set the text and transparency

        Parameters
        ----------
        text: str
            Text of the button
        The remaining parameters are passed into AnimBox init method
        """
        super().__init__(x, y, width, height, parent=parent)
        self.text = text
        self.transparent = False

    def set_transparent(self, state):
        """Make the button transparent

        Parameters
        ----------
        state: bool
            True for transparent, False otherwise
        """
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
        """Reimplement from AnimBox. Calls for AnimBox paint event first, then draw its background and text.
        """
        super().paint(painter, style, widget)
        painter.setPen(self.default_pen)
        if self.transparent:
            painter.fillRect(self.btn_rect, QColor(255, 255, 255, 0.1))
        else:
            painter.fillRect(self.btn_rect, Qt.black)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, self.text)

    def mousePressEvent(self, event):
        """Reimplemented from QGraphicsObject. Receive the click event,
        then reverse its animation and emit buttonClicked signal
        """
        event.accept()
        self.toggle_anim(False)
        self.buttonClicked.emit(self.text)


class MenuButton(AnimBox):
    """Button used in menu. Contains animated text.

    Attributes
    ----------
    buttonClicked: pyqtSignal(str)
        Emitted when it is clicked. Sends the text of the button
    """
    buttonClicked = pyqtSignal(str)

    def __init__(self, x, y, width, height, text, parent=None):
        """Set the text and create AnimatedText

        Parameters
        ----------
        text: str
            Text of the button
        The remaining parameters are passed into AnimBox init method
        """
        super().__init__(x, y, width, height, parent=parent)
        self.text = text
        self.animText = AnimatedText(text, parent=self)

    def paint(self, painter, style, widget=None):
        """Reimplement from AnimBox. Calls for AnimBox paint event first, then draw its background.
        """
        super().paint(painter, style, widget)
        painter.fillRect(self.btn_rect, Qt.black)

    def mousePressEvent(self, event):
        """Reimplemented from QGraphicsObject. Receive the click event,
        then reverse its animation and emit buttonClicked signal
        """
        event.accept()
        self.toggle_anim(False)
        self.buttonClicked.emit(self.text)



