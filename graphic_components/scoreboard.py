"""This module contains the components that makes up the score board. It is constructed using QWigdets
and then embedded into the QGraphicsScene using QGraphicsProxyWidget because it's easier."""

import sys
import os

from PySide2.QtCore import (QAbstractAnimation, Qt, QPropertyAnimation, Property, Signal, QTimer)
from PySide2.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QGridLayout, QVBoxLayout, QPushButton, QLabel, QApplication)

from general import highscore as hs
from .textbox import AnimatedLabel

if not __name__ == "__main__":
    current_dir = os.getcwd()
    sys.path.append(current_dir)
    hs_file = current_dir + "/general/highscore.txt"
else:
    # For testing, maybe wrong
    hs_file = "../general/highscore.txt"


if not os.path.exists(hs_file):
    print('Missing High Score file. Generating one. ')
    hs.generate_highscore_file(hs_file)

BACKWARD = 1
FORWARD = -1


class HighScoreBoard(QWidget):
    highScoreSet = Signal()

    def __init__(self, width, height):
        """Initialise the widget with the specified width and height.

        Parameters
        ----------
        width: float
            width of the widget
        height: float
            height of the widget
        """
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
        self.name_input.setVisible(False)

        self.setFixedSize(width, height)
        self.setStyleSheet("""background-color: rgb(0, 0, 0);
                            color: rgb(255, 255, 255); 
                            """)

        self.diff_switch.difficultySelected.connect(self.change_score_board)
        self.name_input.nameReceived.connect(self.set_score)
        self.score_grid.scoreUpdate.connect(self.diff_switch.go_to_difficulty)

    def change_score_board(self, difficulty):
        """Change to he score board to the corresponding difficulty

        Parameters
        ----------
        difficulty: str
            The difficulty for the score board to change to
        """
        self.score_grid.replace_scores(difficulty)

    def show_scores(self, toggle):
        """Shows the score board in the current difficulty, if the widget is visible

        Parameters
        ----------
        toggle: bool
            True to show the board, False otherwise
        """
        if self.isVisible():
            self.score_grid.show_score_info(toggle)

    def set_score(self, name):
        """Set the high score with an input name, to the current difficulty and time.
        Emits a signal once high score is set.

        Parameters
        ----------
        name: str
            Name for the high score
        """
        self.score_grid.set_highscore(self.current_difficulty, name, self.final_time)
        self.name_input.setVisible(False)
        self.highScoreSet.emit()

    def check_ranking(self, difficulty, time):
        """First, it updates the current difficulty and time. Check if the current time ranks in the Top 5.
        If so, display the score board in the correct difficulty.

        Parameters
        ----------
        difficulty: str
            Current difficulty of the puzzle

        time: str
            The time taken to solve the puzzle

        Returns
        -------
        bool: True if it ranks Top 5, False otherwise
        """
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
    """The layout that contains the switches between the difficulties and displays them.

    Attributes
    ----------
    difficultySelected: Signal(str)
        Emitted when a difficulty is selected. Emits the selected difficulty.
    """
    difficultySelected = Signal(str)

    def __init__(self):
        """Create the full text to cycle through. Then, create the label and the buttons.
        The text is set up such that the last element on the list is additionally inserted in the front
        and the first on the list is additionally appended at the back, like this:
        [4 0 1 2 3 4 0]

        When the cycle reaches the end, it jumps to the second on the new list, and when the cycle reaches the front,
        it jumps to the second last, giving the illusion of a circular selection.

        Note that the text created is reversed to account for animation.
        """
        super().__init__()

        # Make a copy of the difficulty list, insert texts to create the circular text buffer, spaced equally
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

    @Property(int)
    def show_pos(self):
        """
        int : The position of the string to be shown

        When the value is set, the text from the full text is selected and displayed
        """
        return self._shown_length

    @show_pos.setter
    def show_pos(self, value):
        self._shown_length = value
        self.difficulty_display.setText(self.full_text[value:value+self.max_length])

    def shift_difficulty(self, direction):
        """Connected to the buttons. Change the direction, update the next position
        and activate the timer for cycling
        """
        if not self.timer.isActive():
            self.shift_direction = direction
            self.next_pos = self.circular_value(self.next_pos + direction * self.max_length)
            self.timer.start()

    def go_to_difficulty(self, difficulty):
        """Directly go the selected difficulty, with no cycling.

        Parameters
        ----------
        difficulty: str
            The difficulty to tune to
        """
        pos = (hs.DIFFICULTIES[::-1].index(difficulty) + 1) * self.max_length
        self.show_pos = pos
        self.next_pos = pos

    def shift_pos(self):
        """Continuously increase the current string position until the destination position is reached, in which case
        the timer is stopped and difficultySelected signal is emitted.
        """
        self.show_pos = self.circular_value(self.show_pos + self.shift_direction)
        if self.show_pos == self.next_pos:
            self.timer.stop()
            self.difficultySelected.emit(self.difficulty_display.text().strip(' '))

    def circular_value(self, pos):
        """Ensure the value showing the string jumps to the correct position

        Parameters
        ----------
        pos: int
            Position in the text

        Returns
        -------
        int: The adjusted position
        """
        if pos == (len(hs.DIFFICULTIES)+1) * self.max_length:
            pos = self.max_length
        elif pos == 0:
            pos = len(hs.DIFFICULTIES) * self.max_length
        return pos


class ScoreGrid(QGridLayout):
    """The layout that displays the score data.

    Attributes
    ----------
    scoreUpdate: Signal
        Emitted when the score board is updated.
    """
    scoreUpdate = Signal(str)

    def __init__(self):
        """Read the high score file, create the animated labels to contain the data.
        """
        super().__init__()
        try:
            self.highscore_list = hs.read_highscore_file(hs_file)
        except Exception as e:
            raise Exception('Cannot open file', e)

        for i in range(5):
            label = QLabel(str(i+1)+'.')
            self.addWidget(label, i, 0)

        # The labels are created with placeholder text.
        self.animated_labels = []
        for i, name in enumerate('ABCDE'):
            label1 = AnimatedLabel(name)
            label1.setAlignment(Qt.AlignCenter)
            label2 = AnimatedLabel('--:--')
            label2.setAlignment(Qt.AlignRight)
            self.addWidget(label1, i, 1)
            self.addWidget(label2, i, 2)
            self.animated_labels.append(label1)
            self.animated_labels.append(label2)

        self.replace_scores(hs.DIFFICULTIES[0])

    def show_score_info(self, toggle):
        """Animate the label to show/hide the data

        Parameters
        ----------
        toggle: bool
            True to show data, False otherwise
        """
        for label in self.animated_labels:
            label.toggle_anim(toggle)

    def replace_scores(self, difficulty):
        """Replace the current scores with data from the selected difficulty

        Parameters
        ----------
        difficulty: str
            The difficulty to show
        """
        scores = self.highscore_list[difficulty]
        for i in range(len(scores)):
            self.animated_labels[2*i].replace_text(scores[i]['name'])
            self.animated_labels[2*i+1].replace_text(scores[i]['time'])

    def set_highscore(self, difficulty, name, time):
        """Set the high score with the given data

        Parameters
        ----------
        difficulty: str
            The difficulty which the data is set to
        name: str
            Name to be set
        time: str
            Time to be set
        """
        hs.replace_placing(self.highscore_list, difficulty, name, time)
        hs.write_highscore_file(hs_file, self.highscore_list)
        self.replace_scores(difficulty)
        self.scoreUpdate.emit(difficulty)

    def get_rank(self, difficulty, time):
        """Check and get the ranking of a given time and difficulty

        Parameters
        ----------
        difficulty: str
            The difficulty to check for
        time: str
            The time to be compared with

        Returns
        -------
        int: The rank in the Top 5. -1 if it is out of Top 5
        """
        return hs.check_ranking(self.highscore_list, difficulty, time)


class NameInput(QWidget):
    """The widget to input a name for high score. It should be hidden until needed.

    Attributes
    ----------
    nameReceived: Signal(str)
        Emitted once a non-whitespace name is received. Emits the name
    """
    nameReceived = Signal(str)

    def __init__(self):
        """Creates the widget: a label to show the rank and time, and QLineEdit for name input
        """
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
        """Strip the name off whitespaces, and emit it if there is any character
        """
        name = self.name_input.text().strip(' ')
        if name:
            self.nameReceived.emit(name)


if __name__ == '__main__':
    app = 0
    app = QApplication(sys.argv)

    ex = HighScoreBoard(500, 500)
    ex.show()
    sys.exit(app.exec_())
