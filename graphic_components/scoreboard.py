import random
import sys
import os

from PyQt5.Qt import QApplication
from PyQt5.QtCore import (QAbstractAnimation, Qt, QPropertyAnimation, pyqtProperty, pyqtSignal, QTimer)
from PyQt5.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QGridLayout, QVBoxLayout, QPushButton, QLabel)

if not __name__ == "__main__":
    current_dir = os.getcwd()
    sys.path.append(current_dir)
    hs_file = current_dir + "/general/highscore.txt"
else:
    hs_file = "./sudoku/general/highscore.txt"

from general import highscore as hs
from .textbox import AnimatedLabel

if not os.path.exists(hs_file):
    print('Missing High Score file. Generating one. ')
    hs.generate_highscore_file(hs_file)

BACKWARD = 1
FORWARD = -1


class HighScoreBoard(QWidget):
    highScoreSet = pyqtSignal()

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
        self.name_input.setVisible(False)
        self.highScoreSet.emit()

    def check_ranking(self, difficulty, time):
        self.current_difficulty = difficulty
        self.final_time = time
        rank = self.score_grid.get_rank(difficulty, time)
        if rank >= 0:
            self.diff_switch.go_to_difficulty(difficulty)
            self.score_grid.replace_scores(difficulty)
            self.name_input.setVisible(True)
            self.name_input.rank_label.setText(str(rank+1))
            self.name_input.time_display.setText(time)
            return True
        return False


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
        pos = (hs.DIFFICULTIES[::-1].index(difficulty) + 1) * self.max_length
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
            self.highscore_list = hs.read_highscore_file(hs_file)
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
        hs.write_highscore_file(hs_file, self.highscore_list)
        self.replace_scores(difficulty)
        self.scoreUpdate.emit(difficulty)

    def get_rank(self, difficulty, time):
        return hs.check_ranking(self.highscore_list, difficulty, time)


class NameInput(QWidget):
    nameReceived = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)

        self.rank_label = QLabel('-')
        self.layout.addWidget(self.rank_label)

        self.name_input = QLineEdit(self)
        self.name_input.setMaxLength(13)
        self.layout.addWidget(self.name_input)

        self.time_display = QLabel('-:-:-')
        self.layout.addWidget(self.time_display)
        self.name_input.returnPressed.connect(self.receive_name_input)

        self.name_input.setStyleSheet("""
            border-top: 1px solid white;
        """)

    def receive_name_input(self):
        print(self.name_input.text().strip(' '))
        name = self.name_input.text().strip(' ')
        if name:
            self.nameReceived.emit(name)


if __name__ == '__main__':
    app = 0
    app = QApplication(sys.argv)

    ex = HighScoreBoard(500, 500)
    ex.show()
    sys.exit(app.exec_())