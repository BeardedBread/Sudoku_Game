from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QGridLayout, QVBoxLayout, QSizePolicy,
                             QPushButton, QLabel)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal, QSizeF, QTimer)
from PyQt5.Qt import QApplication
import sys
import random

if not __name__ == "__main__":
    sys.path.append("~/PycharmProjects/sudoku")

from general import highscore as hs

BACKWARD = 1
FORWARD = -1

class HighScoreBoard(QWidget):

    def __init__(self, width, height):
        super().__init__()

        self.final_time = "00:10:00"
        self.current_difficulty = hs.DIFFICULTIES[1]
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(QLabel('Score Board', self, alignment=Qt.AlignCenter))
        self.diff_switch = DifficultySwitch()
        self.layout.addLayout(self.diff_switch)
        self.score_grid = ScoreGrid()
        self.layout.addLayout(self.score_grid)
        self.name_input = NameInput()
        self.layout.addWidget(self.name_input)

        self.setFixedSize(width, height)

        self.setStyleSheet("""
                            background-color: rgb(0, 0, 0);
                            color: rgb(255, 255, 255); 
                            """)

        self.name_input.setVisible(False)

        self.diff_switch.difficultySelected.connect(self.change_score_board)
        self.name_input.nameReceived.connect(self.set_score)
        self.score_grid.scoreUpdate.connect(self.diff_switch.go_to_difficulty)

    def change_score_board(self, difficulty):
        self.score_grid.replace_scores(difficulty)

    def show_scores(self, toggle):
        if self.isVisible():
            self.score_grid.show_score_info(toggle)

    def set_score(self, name):
        self.score_grid.set_highscore(self.current_difficulty, name, self.final_time)


class DifficultySwitch(QHBoxLayout):
    difficultySelected = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        circular_text = hs.DIFFICULTIES.copy()
        circular_text.insert(0, hs.DIFFICULTIES[-1])
        circular_text.append(hs.DIFFICULTIES[0])
        self.max_length = max(len(diff) for diff in hs.DIFFICULTIES)
        self.full_text = ''.join(d.center(self.max_length) for d in circular_text[::-1])
        left_btn = QPushButton('<')
        left_btn.setFixedSize(20, 20)
        self.difficulty_display = QLabel('Normal')
        self.difficulty_display.setAlignment(Qt.AlignCenter)
        right_btn = QPushButton('>')
        right_btn.setFixedSize(20, 20)

        self.addWidget(left_btn)
        self.addWidget(self.difficulty_display)
        self.addWidget(right_btn)
        self.layout().setStretch(1, 2)

        self.shift_direction = FORWARD
        self.show_pos = self.max_length * len(hs.DIFFICULTIES)
        self.next_pos = self.max_length * len(hs.DIFFICULTIES)
        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.timeout.connect(self.shift_pos)
        left_btn.clicked.connect(lambda: self.shift_difficulty(BACKWARD))
        right_btn.clicked.connect(lambda: self.shift_difficulty(FORWARD))

    @pyqtProperty(int)
    def show_pos(self):
        """
        int : The value for the animation

        When the value is set, the text to be shown is selected from the full text.
        """
        return self._shown_length

    @show_pos.setter
    def show_pos(self, value):
        self._shown_length = value
        self.difficulty_display.setText(self.full_text[value:value+self.max_length])

    def shift_difficulty(self, direction):
        if not self.timer.isActive():
            self.shift_direction = direction
            self.next_pos = self.circular_value(self.next_pos + direction * self.max_length)
            self.timer.start()

    def go_to_difficulty(self, difficulty):
        pos = (hs.DIFFICULTIES.index(difficulty) + 1) * self.max_length
        self.show_pos = pos
        self.next_pos = pos

    def shift_pos(self):
        self.show_pos = self.circular_value(self.show_pos + self.shift_direction)
        if self.show_pos == self.next_pos:
            self.timer.stop()
            self.difficultySelected.emit(self.difficulty_display.text().strip(' '))

    def circular_value(self, value):
        if value == (len(hs.DIFFICULTIES)+1) * self.max_length:
            value = self.max_length
        elif value == 0:
            value = len(hs.DIFFICULTIES) * self.max_length
        return value


class ScoreGrid(QGridLayout):
    scoreUpdate = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        try:
            self.highscore_list = hs.read_highscore_file("/home/eyt21/PycharmProjects/sudoku/general/highscore.txt")
        except Exception as e:
            print('Cannot open file', e)

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

        self.replace_scores(hs.DIFFICULTIES[0])

    def show_score_info(self, toggle):
        for label in self.animated_labels:
            label.toggle_anim(toggle)

    def replace_scores(self, difficulty):
        scores = self.highscore_list[difficulty]
        for i in range(len(scores)):
            self.animated_labels[2*i].replace_text(scores[i]['name'])
            self.animated_labels[2*i+1].replace_text(scores[i]['time'])

    def set_highscore(self, difficulty, name, time):
        hs.replace_placing(self.highscore_list, difficulty, name, time)
        self.replace_scores(difficulty)
        self.scoreUpdate.emit(difficulty)

class NameInput(QWidget):
    nameReceived = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)

        self.layout.addWidget(QLabel('Name'))

        self.name_input = QLineEdit(self)
        self.layout.addWidget(self.name_input)
        self.name_input.returnPressed.connect(self.receive_name_input)

        self.name_input.setStyleSheet("""
            border: 2px solid gray;
        """)

    def receive_name_input(self):
        print(self.name_input.text().strip(' '))
        name = self.name_input.text().strip(' ')
        if name:
            self.nameReceived.emit(name)


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