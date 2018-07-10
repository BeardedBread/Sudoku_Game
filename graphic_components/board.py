from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import (QSizePolicy, QGraphicsWidget, QGraphicsItem,
                             QGraphicsLineItem, QGraphicsRectItem, QGraphicsObject,
                             QGraphicsItemGroup, QGraphicsPathItem, QGraphicsLinearLayout)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal, QSizeF)

from . import sudoku_graphics as sdk_grap
from . import menu_graphics as menu_grap
from general import extras


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
        #super().paint(painter, style, widget)

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

    def __init__(self, width, height, parent=None):
        super().__init__(width, height, parent)

        self.gamegrid = sdk_grap.SudokuGrid(self.width, self.height, parent=self)
        self.numring = sdk_grap.NumberRing(parent=self)
        self.playmenu = sdk_grap.PlayMenu(parent=self)

        self.show_grid(False)
        self.show_playmenu(False)

        self.gamegrid.buttonClicked.connect(self.show_number_ring)
        self.numring.connect_button_signals(self.select_ring_number)

        self.gamegrid.setFocus(Qt.MouseFocusReason)

        self.anim.finished.connect(lambda: self.show_playmenu(True))
        self.playmenu.buttonClicked.connect(lambda: self.show_grid(True))
        self.toggle_anim(True)

    def show_number_ring(self, x=0, y=0):
        if not self.gamegrid.freeze:
            self.numring.setPos(x, y)
            self.numring.setVisible(True)
            self.numring.setFocus()
        else:
            self.gamegrid.freeze = False
            self.gamegrid.setFocus()

    def select_ring_number(self, val):
        if val == 'X':
            val = 0
        self.gamegrid.replace_cell_number(int(val))
        self.show_number_ring()

    def game_refocus(self):
        self.gamegrid.freeze = False
        self.gamegrid.setFocus()

    def show_grid(self, state):
        self.gamegrid.setVisible(state)
        if state:
            self.gamegrid.toggle_anim(True)

    def show_playmenu(self, state):
        self.playmenu.setVisible(state)


class MenuBoard(BoxBoard):
    """
    The Board that contains menu options. Also contains the timer.
    """

    def __init__(self, width, height, parent=None):
        super().__init__(width, height, parent)

        self.layout = QGraphicsLinearLayout(Qt.Horizontal)
        self.layout.setMinimumWidth(width)
        self.layout.setMinimumWidth(height)

        self.diff_display = menu_grap.DifficultyDisplayer(parent=self)
        self.layout.addItem(self.diff_display)
        self.timer_display = menu_grap.TimerDisplayer(parent=self)
        self.layout.addItem(self.timer_display)
        self.layout.setItemSpacing(0, 50)
        self.layout.setItemSpacing(1, 0)
        self.layout.setContentsMargins(20,15,20,15)

        self.setLayout(self.layout)

        self.show_children(False)
        self.anim.finished.connect(lambda: self.show_children(True))
        self.toggle_anim(True)

    def show_difficulty(self, state):
        print(state)
        self.diff_display.selected = state
        self.diff_display.update()

    def show_children(self, state):
        for chd in self.children():
            chd.setVisible(state)
