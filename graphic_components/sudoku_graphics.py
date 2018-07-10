# Put all Sudoku related graphics here
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsObject
from PyQt5.QtCore import (QAbstractAnimation, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal)

from gameplay import sudoku_gameplay as sdk
from general.extras import bound_value
from graphic_components import buttons
import numpy as np


class BaseSudokuItem(QGraphicsObject):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.default_pen = QPen()
        self.default_pen.setColor(Qt.white)
        self.default_pen.setWidth(1)

        self.freeze = False


class NumberPainter(BaseSudokuItem):
    # TODO: Use different font to differentiate the status of a cell

    def __init__(self, parent, grid):
        super().__init__(parent=parent)
        self.sudoku_grid = grid
        self.invalid_pen = QPen()
        self.invalid_pen.setColor(Qt.lightGray)
        self.invalid_unit = 8
        self.invalid_pen.setWidth(self.invalid_unit)

    def paint(self, painter, style, widget=None):
        for i in range(9):
            for j in range(9):
                self._draw_number_cell(i, j, painter)

    def boundingRect(self):
        return QRectF(-5, -5, self.parent.width+10, self.parent.height+10)

    def _draw_number_cell(self, w, h, painter):
        val = self.sudoku_grid.get_cell_number(h, w)
        if val == 0:
            val = ''
        else:
            if self.sudoku_grid.get_cell_status(h, w) == sdk.VALID:
                painter.setPen(self.default_pen)
            else:
                painter.setPen(self.invalid_pen)

        painter.drawText((w+0.5)*self.parent.cell_width-5,
                         (h+0.5)*self.parent.cell_height+5,
                         str(val))


class SudokuGrid(BaseSudokuItem):
    # TODO: Add functions to animated the grid lines
    buttonClicked = pyqtSignal(float, float)

    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height

        self.thick_pen = QPen()
        self.thick_pen.setColor(Qt.white)
        self.thick_unit = 5
        self.thick_pen.setWidth(self.thick_unit)

        self.thinlines = []
        self.thicklines = []

        self.cell_width = self.width / 9
        self.cell_height = self.height / 9

        for i in range(1, 9):
            delta_h = self.cell_height * i
            delta_w = self.cell_width * i
            if i%3 == 0:
                self.thicklines.append(QLineF(0, delta_h, self.width, delta_h))
                self.thicklines.append(QLineF(delta_w, 0, delta_w, self.height))
            else:
                self.thinlines.append(QLineF(0, delta_h, self.width, delta_h))

                self.thinlines.append(QLineF(delta_w, 0, delta_w, self.height))

        self.sudoku_grid = sdk.SudokuSystem()
        self.grid_painter = NumberPainter(self, self.sudoku_grid)

        self.mouse_w = 0
        self.mouse_h = 0
        self.selection_unit = 8
        self.selection_pen = QPen()
        self.selection_pen.setColor(Qt.white)
        self.selection_pen.setWidth(self.selection_unit)
        self.selection_box = QRectF(0, 0, self.cell_width, self.cell_height)

        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)

        self.freeze = False

    def replace_cell_number(self, val):
        self.sudoku_grid.replace_cell_number(self.mouse_h, self.mouse_w, val)
        self.grid_painter.update()

    def boundingRect(self):
        return QRectF(-5, -5, self.width+10, self.height+10)

    # Reimplemented paint
    def paint(self, painter, style, widget=None):
        painter.setPen(self.default_pen)
        for line in self.thinlines:
            painter.drawLine(line)

        painter.setPen(self.thick_pen)
        for line in self.thicklines:
            painter.drawLine(line)

        painter.setPen(self.selection_pen)
        painter.drawRect(self.selection_box)

        # TODO: Possibly draw the fixed cell here

    def hoverMoveEvent(self, event):
        if not self.freeze:
            box_w = bound_value(0, int(event.pos().x()/self.cell_width), 8)
            box_h = bound_value(0, int(event.pos().y() / self.cell_height), 8)
            if box_w != self.mouse_w or box_h != self.mouse_h:
                self.mouse_w = box_w
                self.mouse_h = box_h
                self.selection_box.moveTopLeft(QPointF(box_w*self.cell_width, box_h*self.cell_height))
                self.update()

    def mousePressEvent(self, event):
        if not self.freeze:
            w = (self.mouse_w + 0.5) * self.cell_width - 5
            h = (self.mouse_h + 0.5) * self.cell_height + 5

            if not self.sudoku_grid.get_cell_status(self.mouse_h, self.mouse_w) == sdk.FIXED:
                self.buttonClicked.emit(w, h)
        else:
            self.buttonClicked.emit(0, 0)


class NumberRing(BaseSudokuItem):
    # TODO: Add functions to animated the ring appearing
    # TODO: Adjust the positioning of each element
    # TODO: Make it transparent when mouse is out of range

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setVisible(False)
        self.radius = 48
        self.cell_width = 24
        self.cell_height = 24

        self.cell_buttons = []
        for i in range(10):
            cell_x = self.radius * np.sin(np.deg2rad(360/10*i)) - self.cell_width/2
            cell_y = - self.radius * np.cos(np.deg2rad(360 / 10 * i)) - self.cell_height/2
            if i == 0:
                cell_string = 'X'
            else:
                cell_string = str(i)
            btn = buttons.animBox(cell_x, cell_y, self.cell_width,
                                  self.cell_height, cell_string, self)

            self.cell_buttons.append(btn)

    def boundingRect(self):
        return QRectF(-5, -5, self.cell_width+self.radius*2+10,
                      self.cell_height + self.radius * 2 + 10)

    # Reimplemented paint
    def paint(self, painter, style, widget=None):
        pass

    def connect_button_signals(self, func):
        for btn in self.cell_buttons:
            btn.buttonClicked.connect(func)
            
    def freeze_buttons(self, state):
        for btn in self.cell_buttons:
            btn.freeze = state
