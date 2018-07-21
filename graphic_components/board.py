from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QSizePolicy, QGraphicsWidget
from PyQt5.QtCore import (QAbstractAnimation, Qt, QLineF, QPropertyAnimation, pyqtProperty,
                          pyqtSignal, QSizeF)

from . import sudoku_graphics as sdk_grap
from . import menu_graphics as menu_grap


class BoxBoard(QGraphicsWidget):
    """
    A generic board that draws an animated rectangular border
    """

    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.half_circumference = width+height
        self.freeze = False

        self.setMinimumSize(QSizeF(width, height))
        #self.setMaximumSize(QSizeF(width, height))

        self.size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.size_policy.setHeightForWidth(True)
        self.setSizePolicy(self.size_policy)

        # Set up a default pen for drawing
        self.default_pen = QPen()
        self.default_pen.setColor(Qt.white)
        self.default_pen.setWidth(5)

        # The 4 lines to construct the box
        self.left = QLineF(0, 0, 0, self.height)
        self.down = QLineF(0, self.height, self.width, self.height)
        self.right = QLineF(self.width, self.height, self.width, 0)
        self.up = QLineF(self.width, 0, 0, 0)

        self.line_order = [self.up, self.right, self.down, self.left]

        # Length of the box to be drawn
        self.length = 0
        # Set up the length to be animated
        self.anim = QPropertyAnimation(self, b'length')
        self.anim.setDuration(800)  # Animation speed
        self.anim.setStartValue(0)
        for t in range(1, 10):
            self.anim.setKeyValueAt(t / 10, self.half_circumference * t/10)
        self.anim.setEndValue(self.half_circumference)

    # Toggle the animation to be play forward or backward
    def toggle_anim(self, toggling):
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    # Reimplemented paint
    def paint(self, painter, style, widget=None):
        painter.setPen(self.default_pen)
        for line in self.line_order:
            if line.length() > 1:
                painter.drawLine(line)

    # Defining the length to be drawn as a pyqtProperty
    @pyqtProperty(float)
    def length(self):
        return self._length

    # Determine the length of the four lines to be drawn
    @length.setter
    def length(self, value):
        self._length = value
        remaining_length = value
        if remaining_length >= self.height:
            length_to_draw = remaining_length - self.height
            remaining_length -= length_to_draw
        else:
            length_to_draw = 0

        self.down.setLine(0, self.height, length_to_draw, self.height)
        self.up.setLine(self.width, 0, self.width - length_to_draw, 0)
        self.left.setLine(0, 0, 0, remaining_length)
        self.right.setLine(self.width, self.height, self.width, self.height - remaining_length)
        self.update()


class GameBoard(BoxBoard):
    """
    The Board in which the main game takes place.
    It is intended to swap the interface depending on whether the game is ongoing
    """
    boxClicked = pyqtSignal(bool)
    newGameSelected = pyqtSignal(str)
    gridDrawn = pyqtSignal()
    sudokuDone = pyqtSignal()

    def __init__(self, width, height, parent=None):
        super().__init__(width, height, parent)

        self.gamegrid = sdk_grap.SudokuGrid(self.width, self.height, parent=self)
        self.numring = sdk_grap.NumberRing(parent=self)
        self.playmenu = sdk_grap.PlayMenu(parent=self)

        self.show_grid(False)
        self.show_playmenu(False)

        self.gamegrid.buttonClicked.connect(self.show_number_ring)
        self.numring.connect_button_signals(self.select_ring_number)
        self.numring.keyPressed.connect(self.select_ring_number)

        self.gamegrid.setFocus(Qt.MouseFocusReason)

        self.anim.finished.connect(lambda: self.show_playmenu(True))
        self.playmenu.buttonClicked.connect(self.new_game)
        self.gamegrid.finishDrawing.connect(self.gridDrawn.emit)
        self.gamegrid.puzzleFinished.connect(self.sudokuDone.emit)
        self.numring.loseFocus.connect(self.game_refocus)
        self.toggle_anim(True)

    def show_number_ring(self, x=0, y=0):
        if not self.numring.isVisible():
            self.numring.setPos(x, y)
            self.numring.setVisible(True)
            self.numring.setFocus()
            self.numring.toggle_anim(True)

    def select_ring_number(self, val):
        if val == 'X':
            val = 0
        self.gamegrid.replace_cell_number(int(val))
        #self.game_refocus()

    def game_refocus(self):
        self.gamegrid.set_disabled(False)
        self.gamegrid.setFocus()

    def show_grid(self, state):
        if state ^ self.gamegrid.isVisible():
            self.gamegrid.setVisible(state)
            if state:
                self.gamegrid.toggle_anim(True)

    def show_playmenu(self, state):
        self.playmenu.setVisible(state)

    def new_game(self, string):
        print('new game selected')
        self.gamegrid.generate_new_grid(menu_grap.DIFFICULTIES.index(string))
        self.show_grid(True)
        self.newGameSelected.emit(string)


class MenuBoard(BoxBoard):
    """
    The Board that contains menu options. Also contains the timer.
    """

    def __init__(self, width, height, parent=None):
        super().__init__(width, height, parent)

        self.margin = 10
        self.spacing = 20
        w_spacing = (self.width - 2*self.margin) /3

        self.diff_display = menu_grap.DifficultyDisplayer(parent=self)
        self.diff_display.setX(self.margin)
        self.diff_display.setY(self.geometry().height()/2-self.diff_display.height/2)
        self.timer_display = menu_grap.TimerDisplayer(parent=self)
        self.timer_display.setParent(self)
        self.timer_display.setX(self.margin + w_spacing + self.spacing)
        self.timer_display.setY(self.geometry().height()/2-self.timer_display.height/2)
        self.score_display = menu_grap.HighScoreDisplayer(parent=self)
        self.score_display.setX(self.width - self.margin)
        self.score_display.setY(self.height - self.margin)

        self.score_display.scoreboard_widget.highScoreSet.connect(self.return_to_normal)

        self.show_children(False)
        self.toggle_anim(True)

    def show_difficulty(self, state):
        self.diff_display.selected = state
        self.diff_display.update()

    def show_children(self, state):
        self.timer_display.setVisible(state)
        self.diff_display.setVisible(state)
        self.timer_display.reset_time()

    def set_difficulty_text(self, string):
        self.diff_display.set_text(string)
        self.timer_display.reset_time()

    def finish_the_game(self):
        self.timer_display.timer.stop()
        diff = self.diff_display.text
        time = self.timer_display.get_time()
        if self.score_display.scoreboard_widget.check_ranking(diff, time):
            self.diff_display.set_disabled(True)
            self.score_display.set_disabled(True)
            self.score_display.show_board(True)

    def return_to_normal(self):
        self.diff_display.set_disabled(False)
        self.score_display.set_disabled(False)
