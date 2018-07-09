from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import (QSizePolicy, QGraphicsWidget, QGraphicsItem,
                             QGraphicsLineItem, QGraphicsRectItem, QGraphicsObject,
                             QGraphicsItemGroup, QGraphicsPathItem, QGraphicsLinearLayout)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal, QSizeF)

from graphic_components import sudoku_graphics as sdk_grap
from graphic_components import menu_graphics as menu_grap

class BoxBoard(QGraphicsWidget):

    # Initialisation
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.circumference = 2*(width+height)
        self.setMinimumSize(QSizeF(width, height))
        self.setMaximumSize(QSizeF(width, height))

        self.size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.size_policy.setHeightForWidth(True)
        self.setSizePolicy(self.size_policy)

        # Set up pens for drawing
        self.default_pen = QPen()
        self.default_pen.setColor(Qt.white)
        self.default_pen.setWidth(5)

        # The 4 lines to construct the box
        self.left = QLineF(0, 0, 0, self.height)
        self.down = QLineF(0, self.height, self.width, self.height)
        self.right = QLineF(self.width, 0, self.width, self.height)
        self.up = QLineF(0, 0, self.width, 0)

        self.line_order = [self.up, self.right, self.down, self.left]

    # Reimplemented boundingRect
    #def boundingRect(self):
    #    return QRectF(-5, -5, self.width+10, self.height+10)

    # Reimplemented paint
    def paint(self, painter, style, widget=None):
        painter.setPen(self.default_pen)
        for line in self.line_order:
            if line.length() > 1:
                painter.drawLine(line)
        #painter.drawRect(self.geometry())
        super().paint(painter, style, widget)

    #def sizeHint(self, which, constraint=None):
    #    super().sizeHint(which, constraint)
    #    return QSizeF(self.width, self.height)


class GameBoard(BoxBoard):

    def __init__(self, width, height, parent=None):
        super().__init__(width, height, parent)

        self.gamegrid = sdk_grap.SudokuGrid(self.width, self.height, parent=self)
        self.numring = sdk_grap.NumberRing(parent=self)

        self.gamegrid.buttonClicked.connect(self.show_number_ring)
        self.numring.connect_button_signals(self.select_ring_number)

    def show_number_ring(self, x=0, y=0):
        if not self.gamegrid.selected:
            self.numring.setPos(x, y)
            self.numring.setVisible(True)
            self.gamegrid.selected = True
        else:
            self.numring.setVisible(False)
            self.gamegrid.selected = False

    def select_ring_number(self, val):
        if val == 'X':
            val = 0
        self.gamegrid.replace_cell_number(int(val))
        self.show_number_ring()


class MenuBoard(BoxBoard):
    # TODO: Create the components for the menu: A timer and a difficulty selector
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

        self.setLayout(self.layout)
