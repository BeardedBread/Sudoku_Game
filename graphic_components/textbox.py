import random

from PyQt5.QtCore import (QAbstractAnimation, Qt, QPropertyAnimation, pyqtProperty)
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QGraphicsObject, QLabel


class AnimatedText(QGraphicsObject):

    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.actual_text = text
        self.shown_text = ''
        self.delay = 3

        # Set up pens for drawing
        self.default_pen = QPen()
        self.default_pen.setColor(Qt.white)

        self.shown_length = 0

        # Set up the length to be animated
        self.anim = QPropertyAnimation(self, b'shown_length')
        self.anim.setDuration(len(self.actual_text) * 50)  # Animation speed
        self.anim.setStartValue(0)
        for t in range(1, 10):
            self.anim.setKeyValueAt(t / 10, (len(self.actual_text) + self.delay) * t/10)
        self.anim.setEndValue(len(self.actual_text) + self.delay)
        self.visibleChanged.connect(self.show_text)

    def show_text(self):
        if self.isVisible():
            self.toggle_anim(True)
        else:
            self.shown_length = 0

    # Toggle the animation to be play forward or backward
    def toggle_anim(self, toggling):
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    def boundingRect(self):
        return self.parent.boundingRect()

    def paint(self, painter, style, widget=None):
        painter.setPen(self.default_pen)
        painter.drawText(self.parent.boundingRect(), Qt.AlignCenter, self.shown_text)

    # Defining the length to be drawn as a pyqtProperty
    @pyqtProperty(int)
    def shown_length(self):
        return self._shown_length

    # Determine the length of the four lines to be drawn
    @shown_length.setter
    def shown_length(self, value):
        self._shown_length = value
        if value < self.delay:
            # All printed text should be garbage
            garbage = [chr(num) for num in
                       [random.choice(range(33, 127)) for _ in range(value)]]
            self.shown_text = ''.join(garbage)
        else:
            # Printed text contain some actual text
            garbage = [chr(num) for num in
                       [random.choice(range(33, 127)) for _ in
                        range(min(len(self.actual_text) + self.delay - value, self.delay))]]
            self.shown_text = self.actual_text[:value - self.delay] + ''.join(garbage)

        self.update()

class AnimatedLabel(QLabel):
    """
    QLabel that a message, which is displayed through animation.
    """

    def __init__(self, text, speed=75, delay=20, parent=None):
        """
        Does some text processing, and set up the animation to display the text

        Parameters
        ----------
        text: str
            Text to be displayed
        speed : int
            The period at which a new character is printed
            The total time is calculated as length of text * speed
            0 means instant display, like a regular QLabel.
        delay : int
            The number of garbage to be printed before printing the actual text
        parent: QWidget
            Pass into QLabel init method
        """
        super().__init__(text, parent)

        self.speed = speed

        self.setWordWrap(True)
        self.setContentsMargins(0, 0, 0, 0)
        # Text processing
        # Make sure the garbage does not exceed the length of actual text
        self.actual_text = text
        self.shown_text = ''
        if delay >= 0:
            self.delay = min(delay, len(self.actual_text))
        else:
            self.delay = len(self.actual_text)

        # Find out where the new paragraphs are so that it is retained
        self.splitpoints = []
        current_point = 0
        line_splits = self.actual_text.split('\n')
        for line in line_splits:
            current_point += len(line)
            self.splitpoints.append(current_point)
            current_point += 1

        # Set up the shown text length to be animated
        self.shown_length = 0
        self.anim = QPropertyAnimation(self, b'shown_length')
        self.anim.setDuration(len(self.actual_text) * speed)
        self.anim.setStartValue(0)
        self.anim.setEndValue(len(self.actual_text) + self.delay)

        #self.setStyleSheet("""
        #            color: rgb(0, 255, 0);
        #        """)
        self.toggle_anim(True)

    @pyqtProperty(int)
    def shown_length(self):
        """
        int : The value for the animation

        When the value is set, the text to be printed is generated accordingly.
        It determines whether actual text is to be printed, and retains the
        paragraphs when printing garbage.
        """
        return self._shown_length

    @shown_length.setter
    def shown_length(self, value):
        self._shown_length = value

        if value < self.delay:
            # All printed text should be garbage
            garbage = [chr(num) for num in
                       [random.choice(range(33, 127)) for _ in range(value)]]

            # Retain the paragraphs
            for num in self.splitpoints[:-1]:
                if num < value:
                    garbage[num] = '\n'

            self.setText(''.join(garbage))
        else:
            # Printed text contain some actual text
            garbage = [chr(num) for num in
                       [random.choice(range(33, 127)) for _ in
                        range(min(len(self.actual_text) + self.delay - value, self.delay))]]

            # Retain the paragraphs, but offset by the number of actual text
            non_garbage = value - self.delay
            for num in self.splitpoints[:-1]:
                if num - non_garbage > 0 and num < value:
                    garbage[num - non_garbage] = '\n'

            self.setText(self.actual_text[:value - self.delay] + ''.join(garbage))

    def toggle_anim(self, toggling):
        """
        Toggle the animation to be play forward or backward

        Parameters
        ----------
        toggling: bool
            True for forward, False for backward
        """
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    def replace_text(self, new_text):
        self.shown_length = 0
        self.actual_text = new_text
        self.anim.setDuration(len(self.actual_text) * self.speed)
        self.anim.setEndValue(len(self.actual_text) + self.delay)
        self.toggle_anim(True)
