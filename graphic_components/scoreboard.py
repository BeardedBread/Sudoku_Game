from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QGridLayout, QVBoxLayout,
                             QPushButton, QLabel)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal, QSizeF, QTimer)
from PyQt5.Qt import QApplication
import sys
import random

if not __name__ == "__main__":
    sys.path.append("~/PycharmProjects/sudoku")

from general import highscore as hs

class HighScoreBoard(QWidget):

    def __init__(self, width, height):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(DifficultySwitch())
        self.score_grid = ScoreGrid()
        self.layout.addLayout(self.score_grid)
        self.layout.addWidget(NameInput())

        self.setFixedSize(width, height)

        self.setStyleSheet("""
                            background-color: rgb(0, 0, 0);
                            color: rgb(255, 255, 255); 
                            """)

    def show_scores(self, toggle):
        self.score_grid.show_score_info(toggle)


class DifficultySwitch(QHBoxLayout):

    def __init__(self):
        super().__init__()

        self.max_length = max(len(diff) for diff in hs.DIFFICULTIES)
        self.full_text = ''.join(d.center(self.max_length) for d in hs.DIFFICULTIES)

        left_btn = QPushButton('<')
        self.difficulty_display = QLabel('Normal')
        self.difficulty_display.setAlignment(Qt.AlignCenter)
        right_btn = QPushButton('>')

        self.addWidget(left_btn)
        self.addWidget(self.difficulty_display)
        self.addWidget(right_btn)

        self.show_pos = 0
        self.reach_end = True
        self.anim = QPropertyAnimation(self, b'show_pos')
        self.anim.setDuration((len(hs.DIFFICULTIES) - 1) * self.max_length * 20)
        self.anim.setStartValue(0)
        self.anim.setEndValue((len(hs.DIFFICULTIES) - 1) * self.max_length)
        left_btn.clicked.connect(lambda: self.shift_difficulty(QAbstractAnimation.Backward))
        right_btn.clicked.connect(lambda: self.shift_difficulty(QAbstractAnimation.Forward))
        self.anim.valueChanged.connect(self.pause_anim)

    @pyqtProperty(int)
    def show_pos(self):
        """
        int : The value for the animation

        When the value is set, the text to be printed is generated accordingly.
        It determines whether actual text is to be printed, and retains the
        paragraphs when printing garbage.
        """
        return self._shown_length

    @show_pos.setter
    def show_pos(self, value):
        self._shown_length = value
        self.difficulty_display.setText(self.full_text[value:value+9])

    def shift_difficulty(self, direction):
        if not self.anim.state() == QAbstractAnimation.Running:
            if (direction == QAbstractAnimation.Forward and self.show_pos < self.anim.endValue()) \
             or (direction == QAbstractAnimation.Backward and self.show_pos > self.anim.startValue()):
                self.anim.setDirection(direction)
                if self.anim.state() == QAbstractAnimation.Paused:
                    self.anim.resume()
                else:
                    self.anim.start()

    def pause_anim(self, value):
        if value % 9 == 0:
            if value == self.anim.endValue() or value == self.anim.endValue():
                self.reach_end = True
            else:
                self.anim.pause()


class ScoreGrid(QGridLayout):

    def __init__(self):
        super().__init__()

        for i in range(5):
            label = QLabel(str(i+1)+'.')
            self.addWidget(label, i, 0)

        self.animated_labels = []
        for i, name in enumerate('ABCDE'):
            label1 = AnimatedLabel(name * 7)
            label1.setAlignment(Qt.AlignCenter)
            label2 = AnimatedLabel('0'*5)
            label2.setAlignment(Qt.AlignRight)
            self.addWidget(label1, i, 1)
            self.addWidget(label2, i, 2)
            self.animated_labels.append(label1)
            self.animated_labels.append(label2)

    def show_score_info(self, toggle):
        for label in self.animated_labels:
            label.toggle_anim(toggle)


class NameInput(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)

        self.layout.addWidget(QLabel('Name'))

        self.name_input = QLineEdit(self)
        self.layout.addWidget(self.name_input)


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


if __name__ == '__main__':
    app = 0
    app = QApplication(sys.argv)

    ex = HighScoreBoard(500, 500)
    ex.show()
    sys.exit(app.exec_())