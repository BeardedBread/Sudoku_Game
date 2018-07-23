"""
This module contains the components that make up the Sudoku Board
"""

import numpy as np
from PyQt5.QtCore import (QAbstractAnimation, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal)
from PyQt5.QtGui import QPen, QFont
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsObject

from gameplay import sudoku_gameplay as sdk
from general.extras import bound_value
from . import buttons
from . import menu_graphics as menu_grap

SCRIBBLE_KEY = Qt.Key_M


class BaseSudokuItem(QGraphicsObject):

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setParent(parent)
        self.parent = parent
        self.default_pen = QPen()
        self.default_pen.setColor(Qt.white)
        self.default_pen.setWidth(1)
        self.default_font = QFont("Helvetica", pointSize=14)

        self.freeze = False


class NumberPainter(BaseSudokuItem):
    # TODO: Use different font to differentiate the status of a cell

    def __init__(self, parent, grid):
        super().__init__(parent=parent)
        self.sudoku_grid = grid

        self.invalid_pen = QPen()
        self.invalid_pen.setColor(Qt.lightGray)
        self.invalid_font = QFont("Helvetica", pointSize=11, italic=True)

        self.fixed_pen = QPen()
        self.fixed_pen.setColor(Qt.white)
        self.fixed_font = QFont("Helvetica", pointSize=18, weight=QFont.Bold)

        self.scribble_font = QFont("Helvetica", pointSize=8)

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
            status = self.sudoku_grid.get_cell_status(h, w)
            if status == sdk.VALID:
                painter.setPen(self.default_pen)
                painter.setFont(self.default_font)
            elif status == sdk.FIXED:
                painter.setPen(self.fixed_pen)
                painter.setFont(self.fixed_font)
            else:
                painter.setPen(self.invalid_pen)
                painter.setFont(self.invalid_font)

        painter.drawText(QRectF(w*self.parent.cell_width, h*self.parent.cell_height,
                                self.parent.cell_width, self.parent.cell_height), Qt.AlignCenter, str(val))

        painter.setPen(self.default_pen)
        painter.setFont(self.scribble_font)
        radius = 15
        for scrib in self.sudoku_grid.scribbles[h, w]:
            num = int(scrib)
            num_x = radius * np.sin(np.deg2rad(360/10*num)) + w * self.parent.cell_width
            num_y = - radius * np.cos(np.deg2rad(360 / 10 * num)) + h * self.parent.cell_height
            painter.drawText(QRectF(num_x, num_y, self.parent.cell_width, self.parent.cell_height),
                             Qt.AlignCenter, scrib)


class SudokuGrid(BaseSudokuItem):
    buttonClicked = pyqtSignal(float, float, bool)
    finishDrawing = pyqtSignal()
    puzzleFinished = pyqtSignal()

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
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.set_disabled(False)

        # Length of the box to be drawn
        self.length = 0
        # Set up the length to be animated
        self.anim = QPropertyAnimation(self, b'length')
        self.anim.setDuration(500)  # Animation speed
        self.anim.setStartValue(0)
        for t in range(1, 10):
            self.anim.setKeyValueAt(t / 10, self.width * t/10)
        self.anim.setEndValue(self.width)

        self.scribbling = False

        self.drawn = False
        self.anim.finished.connect(self.finish_drawing)

    def set_disabled(self, state):
        if state:
            self.setAcceptedMouseButtons(Qt.NoButton)
        else:
            self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(not state)

    def finish_drawing(self):
        if self.length == self.width:
            self.drawn = True
            self.finishDrawing.emit()

    # Toggle the animation to be play forward or backward
    def toggle_anim(self, toggling):
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    def generate_new_grid(self, difficulty):
        self.sudoku_grid.generate_random_board(difficulty)
        #self.sudoku_grid.generate_test_board(difficulty)   # Uncomment for testing
        self.update()

    def change_cell_scribbles(self, val):
        if val == 0:
            self.sudoku_grid.clear_scribble(self.mouse_h, self.mouse_w)
        else:
            self.sudoku_grid.toggle_scribble(self.mouse_h, self.mouse_w, val)
        self.grid_painter.update()

    def replace_cell_number(self, val):
        self.sudoku_grid.replace_cell_number(self.mouse_h, self.mouse_w, val)
        self.grid_painter.update()
        if self.sudoku_grid.completion_check():
            self.puzzleFinished.emit()

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

        if self.drawn:
            painter.setPen(self.selection_pen)
            painter.drawRect(self.selection_box)

    def hoverMoveEvent(self, event):
        if not (self.freeze and self.drawn):
            box_w = bound_value(0, int(event.pos().x()/self.cell_width), 8)
            box_h = bound_value(0, int(event.pos().y() / self.cell_height), 8)
            if box_w != self.mouse_w or box_h != self.mouse_h:
                self.mouse_w = box_w
                self.mouse_h = box_h
                self.selection_box.moveTopLeft(QPointF(box_w*self.cell_width, box_h*self.cell_height))
                self.update()

    def mousePressEvent(self, event):
        event.accept()
        #if self.drawn:
        #    w = (self.mouse_w + 0.5) * self.cell_width
        #    h = (self.mouse_h + 0.5) * self.cell_height

        #    if not self.sudoku_grid.get_cell_status(self.mouse_h, self.mouse_w) == sdk.FIXED:
        #        self.buttonClicked.emit(w, h, self.scribbling)
        #else:
        #    self.buttonClicked.emit(0, 0, self.scribbling)

    def mouseReleaseEvent(self, event):
        if self.drawn:
            w = (self.mouse_w + 0.5) * self.cell_width
            h = (self.mouse_h + 0.5) * self.cell_height

            if not self.sudoku_grid.get_cell_status(self.mouse_h, self.mouse_w) == sdk.FIXED:
                self.buttonClicked.emit(w, h, self.scribbling)
        else:
            self.buttonClicked.emit(0, 0, self.scribbling)

    def focusInEvent(self, event):
        self.set_disabled(False)

    def focusOutEvent(self, event):
        self.set_disabled(True)

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            if (event.key() == SCRIBBLE_KEY) and not self.scribbling:
                self.scribbling = True

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            if event.key() == SCRIBBLE_KEY and self.scribbling:
                self.scribbling = False

    # Defining the length to be drawn as a pyqtProperty
    @pyqtProperty(float)
    def length(self):
        return self._length

    # Determine the length of the four lines to be drawn
    @length.setter
    def length(self, value):
        self._length = value

        for lines in self.thinlines:
            if lines.x1() == 0:
                lines.setP2(QPointF(value, lines.y2()))
            else:
                lines.setP2(QPointF(lines.x2(), value))

        for lines in self.thicklines:
            if lines.x1() == 0:
                lines.setP2(QPointF(value, lines.y2()))
            else:
                lines.setP2(QPointF(lines.x2(), value))

        self.update()


class NumberRing(BaseSudokuItem):
    loseFocus = pyqtSignal()
    keyPressed = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setVisible(False)
        self.cell_width = 24
        self.cell_height = 24

        self.cell_buttons = []
        for i in range(10):
            if i == 0:
                cell_string = 'X'
            else:
                cell_string = str(i)
            btn = buttons.RingButton(0, 0, self.cell_width, self.cell_height,
                                     cell_string, parent=self)
            btn.buttonClicked.connect(self.send_button_press)
            self.cell_buttons.append(btn)

        self.radius = 54
        # Set up the radius to be animated
        self.anim = QPropertyAnimation(self, b'radius')
        self.anim.setDuration(100)  # Animation speed
        self.anim.setStartValue(0)
        for t in range(1, 10):
            self.anim.setKeyValueAt(t / 10, self.radius * t / 10)
        self.anim.setEndValue(self.radius)
        self.anim.finished.connect(self.finish_animation)

        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)

        self.freeze_buttons(True)
        self.scribbling = False

    def finish_animation(self):
        if self.radius == 0:
            self.setVisible(False)
            self.freeze_buttons(True)
            self.loseFocus.emit()
        else:
            self.freeze_buttons(False)
            if self.isUnderMouse():
                self.set_buttons_transparent(False)
            else:
                self.set_buttons_transparent(True)

    # Toggle the animation to be play forward or backward
    def toggle_anim(self, toggling):
        self.freeze_buttons(True)
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    def boundingRect(self):
        return QRectF(-5-self.radius-self.cell_width/2, -5-self.radius-self.cell_height/2,
                      self.cell_width+self.radius*2+10, self.cell_height + self.radius * 2 + 10)

    # Reimplemented paint
    def paint(self, painter, style, widget=None):
        pass

    def send_button_press(self, val):
        self.keyPressed.emit(val, self.scribbling)
        self.close_menu()
            
    def freeze_buttons(self, freeze):
        for btn in self.cell_buttons:
            btn.set_freeze(freeze)

    def focusOutEvent(self, event):
        if not any(btn.isUnderMouse() for btn in self.cell_buttons):
            self.toggle_anim(False)
        else:
            self.setFocus()

    def mousePressEvent(self, event):
        if not any(btn.isUnderMouse() for btn in self.cell_buttons):
            self.toggle_anim(False)
        else:
            self.setFocus()

    def close_menu(self):
        if not self.scribbling:
            self.toggle_anim(False)

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            if (event.key() == SCRIBBLE_KEY) and not self.scribbling:
                self.scribbling = True
            if event.key() == 88:
                txt = 'X'
            elif 49 <= event.key() <= 57:
                txt = str(event.key()-48)
            else:
                txt = ''

            if txt:
                self.keyPressed.emit(txt, self.scribbling)
                if not self.scribbling:
                    self.toggle_anim(False)
                    self.clearFocus()

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            if event.key() == SCRIBBLE_KEY and self.scribbling:
                self.scribbling = False

    def hoverEnterEvent(self, event):
        self.set_buttons_transparent(False)

    def hoverLeaveEvent(self, event):
        self.set_buttons_transparent(True)

    def set_buttons_transparent(self, state):
        for btn in self.cell_buttons:
            btn.set_transparent(state)

    # Defining the length to be drawn as a pyqtProperty
    @pyqtProperty(float)
    def radius(self):
        return self._radius

    # Determine the length of the four lines to be drawn
    @radius.setter
    def radius(self, value):
        self._radius = value

        for i, btn in enumerate(self.cell_buttons):
            cell_x = value * np.sin(np.deg2rad(360/10*i)) - self.cell_width/2
            cell_y = - value * np.cos(np.deg2rad(360 / 10 * i)) - self.cell_height/2

            btn.setX(cell_x)
            btn.setY(cell_y)

        self.update()


class PlayMenu(BaseSudokuItem):
    buttonClicked = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.rect = self.parent.boundingRect()

        self.diff_select = menu_grap.DifficultyMenu(self.rect.width()/2, self.rect.height()/8, self)
        self.diff_select.setX(self.rect.width()/4)
        self.diff_select.setY((self.rect.height() - self.diff_select.height)/2)
        self.diff_select.menuClicked.connect(self.difficulty_selected)

    def paint(self, painter, style, widget=None):
        painter.setPen(self.default_pen)
        painter.setFont(self.default_font)
        painter.drawText(self.rect, Qt.AlignHCenter, 'Select A Difficulty')

    def boundingRect(self):
        return self.diff_select.boundingRect()

    def difficulty_selected(self, string):
        self.setVisible(False)
        self.buttonClicked.emit(string)
