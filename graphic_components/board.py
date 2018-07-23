"""This module contains the two boards shown in the program. A base BoxBoard class provides the drawing and animation
of the boards."""

from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QSizePolicy, QGraphicsWidget
from PyQt5.QtCore import (QAbstractAnimation, Qt, QLineF, QPropertyAnimation, pyqtProperty,
                          pyqtSignal, QSizeF, QRectF)

from . import sudoku_graphics as sdk_grap
from . import menu_graphics as menu_grap


class BoxBoard(QGraphicsWidget):
    """A generic board that draws an animated rectangular border
    """

    def __init__(self, width, height, parent=None):
        """Prepare the lines to be drawn and set up the animation

        Parameters
        ----------
        width: float
            Width of the box
        height: float
            Height of the box
        parent: object
            Pass into QGraphicsWidget init method
        """
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

        self.length = 0
        # Set up the length to be animated
        self.anim = QPropertyAnimation(self, b'length')
        self.anim.setDuration(800)  # Animation speed
        self.anim.setStartValue(0)
        for t in range(1, 10):
            self.anim.setKeyValueAt(t / 10, self.half_circumference * t/10)
        self.anim.setEndValue(self.half_circumference)

    # Defining the length to be drawn as a pyqtProperty
    @pyqtProperty(float)
    def length(self):
        """float: The length of the box to be drawn

        When the value is set, the length of the lines making up the box
        are calculated and updated.
        """
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

    def toggle_anim(self, toggling):
        """Toggle the animation forward and backwards

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

    def paint(self, painter, style, widget=None):
        """Reimplemented from QGraphicsWdiget paint function. Draws the lines making up the box.
        """
        painter.setPen(self.default_pen)
        for line in self.line_order:
            if line.length() > 1:
                painter.drawLine(line)




class GameBoard(BoxBoard):
    """The Board in which the main game takes place.
    It is intended to swap the interface depending on whether the game is ongoing

    Attributes
    ----------
    newGameSelected: pyqtSignal(str)
        Emitted when the difficulty is selected from here. Emits the difficulty string
    gridDrawn: pyqtSignal
        Emitted when the Sudoku grid has been drawn
    sudokuDone: pyqtSignal
        Emitted when the Sudoku puzzle is finished
    """
    newGameSelected = pyqtSignal(str)
    gridDrawn = pyqtSignal()
    sudokuDone = pyqtSignal()

    def __init__(self, width, height, parent=None):
        """Create the game area consisting of a Sudoku Grid and a Number Ring,
        and a difficulty selector at startup

        Parameters
        ----------
        width: float
            Passed into BoxBoard init method
        height: float
            Passed into BoxBoard init method
        parent: object
            Passed into BoxBoard init method
        """
        super().__init__(width, height, parent)

        self.gamegrid = sdk_grap.SudokuGrid(self.width, self.height, parent=self)
        self.numring = sdk_grap.NumberRing(parent=self)
        self.playmenu = sdk_grap.PlayMenu(parent=self)

        self.gamegrid.setFocus(Qt.MouseFocusReason)
        self.show_grid(False)
        self.show_playmenu(False)

        self.gamegrid.buttonClicked.connect(self.show_number_ring)
        self.gamegrid.finishDrawing.connect(self.gridDrawn.emit)
        self.gamegrid.puzzleFinished.connect(self.sudokuDone.emit)
        self.numring.loseFocus.connect(self.game_refocus)
        self.numring.keyPressed.connect(self.select_ring_number)
        self.playmenu.buttonClicked.connect(self.new_game)

        self.anim.finished.connect(lambda: self.show_playmenu(True))
        self.toggle_anim(True)

    def show_number_ring(self, x=0, y=0, scribbling=False):
        """Display the Number Ring if it is not visible, while setting the focus to it

        Parameters
        ----------
        x: float
            x coordinate of where to position the Ring
        y: float
            y coordinate of where to position the Ring
        scribbling:
            True to set Scribble mode, False otherwise
        """
        if not self.numring.isVisible():
            self.numring.setPos(x, y)
            self.numring.setVisible(True)
            self.numring.setFocus()
            self.numring.toggle_anim(True)
            self.numring.scribbling = scribbling


    def select_ring_number(self, val, scribbling):
        """Get the selected number from the Ring and pass into the grid

        Parameters
        ----------
        val: str
            The number string received
        scribbling: bool
            True to indicate Scribble mode, False otherwise
        """
        if val == 'X':
            val = 0
        if scribbling:
            self.gamegrid.change_cell_scribbles(val)
        else:
            self.gamegrid.replace_cell_number(int(val))

    def game_refocus(self):
        """Enable the grid and give it grid focus
        """
        self.gamegrid.set_disabled(False)
        self.gamegrid.setFocus()
        self.gamegrid.scribbling = self.numring.scribbling  # To update the grid scribbling mode

    def show_grid(self, state):
        """Show the grid, if it is not; Hide the grid, if it is.
        Note: Animation only plays when showing the grid.

        Parameters
        ----------
        state: bool
            True to show the grid, False otherwise
        """
        if state ^ self.gamegrid.isVisible():
            self.gamegrid.setVisible(state)
            if state:
                self.gamegrid.toggle_anim(True)

    def show_playmenu(self, state):
        """Show the startup play menu

        Parameters
        ----------
        state: bool
            True to show the startup play menu, False otherwise
        """
        self.playmenu.setVisible(state)

    def new_game(self, string):
        """Generate a new Sudoku Board, given the difficulty

        Parameters
        ----------
        string: str
            The difficulty e.g. Easy
        """
        self.gamegrid.generate_new_grid(menu_grap.DIFFICULTIES.index(string))
        self.show_grid(True)
        self.newGameSelected.emit(string)

    def paint(self, painter, style, widget=None):
        """Reimplemented from BoxBoard paint method. Draw the instruction to toggle scribble mode """
        super().paint(painter, style, widget)

        painter.drawText(QRectF(0, self.height+15, self.width, 15), Qt.AlignCenter,
                         "Hold M to scribble down numbers in a cell")


class MenuBoard(BoxBoard):
    """The Board that contains difficulty options, timer, and high scores.
    """

    def __init__(self, width, height, parent=None):
        super().__init__(width, height, parent)

        self.margin = 10
        self.spacing = 20
        w_spacing = (self.width - 2*self.margin) / 3

        # Create the components and manually position them
        # Not bothered to use the layout item
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

    def show_children(self, state):
        """Show the timer and the difficulty button

        Parameters
        ----------
        state: bool
            True to show them, False otherwise
        """
        self.timer_display.setVisible(state)
        self.diff_display.setVisible(state)
        self.timer_display.reset_time()

    def set_difficulty_text(self, string):
        """Change the difficulty to be display and reset the timer
        """
        self.diff_display.set_text(string)
        self.timer_display.reset_time()

    def finish_the_game(self):
        """Stop the timer and prepare the high scores if necessary. Should only happen when the puzzle is finished
        """
        self.timer_display.timer.stop()
        diff = self.diff_display.text
        time = self.timer_display.get_time()
        if self.score_display.scoreboard_widget.check_ranking(diff, time):
            self.diff_display.set_disabled(True)
            self.score_display.set_disabled(True)
            self.score_display.show_board(True)

    def return_to_normal(self):
        """Reenable the difficulty and high score buttons. Used after setting the high scores"""
        self.diff_display.set_disabled(False)
        self.score_display.set_disabled(False)
