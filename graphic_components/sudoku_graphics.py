"""
This module contains the components that make up the Sudoku Board
"""

import numpy as np
from PySide2.QtCore import (QAbstractAnimation, QPointF, Qt, QRectF, QLineF, QPropertyAnimation, Property, Signal)
from PySide2.QtGui import QPen, QFont
from PySide2.QtWidgets import QGraphicsItem, QGraphicsObject

from gameplay import sudoku_gameplay as sdk
from general.extras import bound_value
from . import buttons
from . import menu_graphics as menu_grap

# This key allows player to scribble on the board
SCRIBBLE_KEY = Qt.Key_M


class BaseSudokuItem(QGraphicsObject):

    def __init__(self, parent):
        """The base class to all Sudoku objects. Provides the default pen and font.
        The parent argument is passed into QGraphicsObject init method.
        Parameters
        ----------
        default_pen: QPen
            The default pen used for drawing. White with line width of 1.
        default_font: QFont
            Default font to use when drawing text. Helvetica, size 14
        freeze: bool
            Whether the object is frozen, i.e. stop responding to user input
        """
        super().__init__(parent=parent)
        self.setParent(parent)
        self.parent = parent
        self.default_pen = QPen()
        self.default_pen.setColor(Qt.white)
        self.default_pen.setWidth(1)
        self.default_font = QFont("Helvetica", pointSize=14)

        self.freeze = False


class NumberPainter(BaseSudokuItem):
    """The object to print the digits present in the grid. Does not draw the actual grids.
    Used as the component for SudokuGrid
    """

    def __init__(self, parent, grid):
        """Initialise different pens to represent the status of a digit.
        The parent argument is passed into BaseSudokuItem init method.

        Parameters
        ----------
        grid: SudokuSystem class
            The class which can be found in gameplay/sudoku_gameplay.py. As objects are passed by reference
            in python, any changes to the SudokuSystem are reflected when this object is repainted.
        """
        super().__init__(parent=parent)
        self.sudoku_grid = grid

        # Used for invalid digits due to the rules
        self.invalid_pen = QPen()
        self.invalid_pen.setColor(Qt.lightGray)
        self.invalid_font = QFont("Helvetica", pointSize=11, italic=True)

        # Used for fixed digits set by the game
        self.fixed_pen = QPen()
        self.fixed_pen.setColor(Qt.white)
        self.fixed_font = QFont("Helvetica", pointSize=18, weight=QFont.Bold)

        # Used for scribbled digits by the player
        self.scribble_font = QFont("Helvetica", pointSize=8)

    def paint(self, painter, style, widget=None):
        """Reimplemented from QGraphicsObject to paint the digits
        """
        for i in range(9):
            for j in range(9):
                self._draw_number_cell(i, j, painter)

    def boundingRect(self):
        """Reimplemented from QGraphicsObject
        """
        return QRectF(-5, -5, self.parent.width+10, self.parent.height+10)

    def _draw_number_cell(self, w, h, painter):
        """Draw the digits(including scribbles) in a given cell, applying the correct pen depending
        on the status of the cell

        Parameters
        ----------
        w: int
            horizontal cell number
        h: int
            vertical cell number
        painter: QPainter
            Used to actually draw the digits
        """
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

        # Scribbles are drawn as a circle, surrounding the cell digit
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
    """The actual grid itself. Handles user input and interfaces the different graphics components.
    Attributes
    ----------
    buttonClicked : Signal(float, float, bool)
        Emitted when click on the grid. Emits the click position and whether the player is scribbling
    finishDrawing : Signal()
        Emitted when the drawing animation ends
    puzzleFinished : Signal()
        Emitted when the puzzle is completed
    """
    buttonClicked = Signal(float, float, bool)
    finishDrawing = Signal()
    puzzleFinished = Signal()

    def __init__(self, width, height, parent=None):
        """Initialise the lines and animation to draw the grid, as well as initialising the
        graphics components. The parent argument is passed into BaseSudokuItem init method.

        Parameters
        ----------
        width: float
            Width of the grid
        height: float
            Height of the grid
        """
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

        # Set up the animation
        self.length = 0
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
        """Disable or Enable the grid to accept inputs

        Parameters
        ----------
        state: bool
            If true, enable the grid. Disable otherwise.
        """
        if state:
            self.setAcceptedMouseButtons(Qt.NoButton)
        else:
            self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setAcceptHoverEvents(not state)

    def finish_drawing(self):
        """Function to be called once the animaion finishes. Emits the finishDrawing signal
        """
        if self.length == self.width:
            self.drawn = True
            self.finishDrawing.emit()

    def toggle_anim(self, toggling):
        """Toggle the animation to be play forward or backward
        """
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    def generate_new_grid(self, difficulty):
        """Generate a new puzzle and update the grid

        Parameters
        ----------
        difficulty: int
            The difficulty level
        """
        self.sudoku_grid.generate_random_board(difficulty)
        #self.sudoku_grid.generate_test_board(difficulty)   # Uncomment for testing
        self.update()

    def change_cell_scribbles(self, val):
        """Change the scribble of a digit of a given cell at the mouse position

        Parameters
        ----------
        val: int
            The scribbled digit to toggle. 0 to clear all
        """
        if val == 0:
            self.sudoku_grid.clear_scribble(self.mouse_h, self.mouse_w)
        else:
            self.sudoku_grid.toggle_scribble(self.mouse_h, self.mouse_w, val)
        self.grid_painter.update()

    def replace_cell_number(self, val):
        """Replaces the digit in a given cell at the mouse position

        Parameters
        ----------
        val: int
            The digit for replacing
        """
        self.sudoku_grid.replace_cell_number(self.mouse_h, self.mouse_w, val)
        self.grid_painter.update()
        if self.sudoku_grid.completion_check():
            self.puzzleFinished.emit()

    def boundingRect(self):
        """Reimplemented from QGraphicsObject
        """
        return QRectF(-5, -5, self.width+10, self.height+10)

    def paint(self, painter, style, widget=None):
        """Reimplemented from QGraphicsObject. Draws the grid lines and the selection box, which follows the mouse.
        """
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
        """Reimplemented from QGraphicsObject. Updates the mouse grid coordinates as long as the grid is drawn
        is not frozen.
        """
        if (not self.freeze) and self.drawn:
            box_w = bound_value(0, int(event.pos().x()/self.cell_width), 8)
            box_h = bound_value(0, int(event.pos().y() / self.cell_height), 8)
            if box_w != self.mouse_w or box_h != self.mouse_h:
                self.mouse_w = box_w
                self.mouse_h = box_h
                self.selection_box.moveTopLeft(QPointF(box_w*self.cell_width, box_h*self.cell_height))
                self.update()

    def mousePressEvent(self, event):
        """Reimplemented from QGraphicsObject. May be useless
        """
        event.accept()

    def mouseReleaseEvent(self, event):
        """Reimplemented from QGraphicsObject. Emits buttonCLicked signal once the player releases the mouse button.
        """
        if self.drawn:
            w = (self.mouse_w + 0.5) * self.cell_width
            h = (self.mouse_h + 0.5) * self.cell_height

            if not self.sudoku_grid.get_cell_status(self.mouse_h, self.mouse_w) == sdk.FIXED:
                self.buttonClicked.emit(w, h, self.scribbling)
        else:
            self.buttonClicked.emit(0, 0, self.scribbling)

    def focusInEvent(self, event):
        """Reimplemented from QGraphicsObject. Unfreeze the grid on focus
        """
        self.set_disabled(False)

    def focusOutEvent(self, event):
        """Reimplemented from QGraphicsObject. Freeze the grid when out of focus
        """
        self.set_disabled(True)

    def keyPressEvent(self, event):
        """Reimplemented from QGraphicsObject. Check if scribble key is held, toggling on scribbling mode.
        """
        if not event.isAutoRepeat():
            if (event.key() == SCRIBBLE_KEY) and not self.scribbling:
                self.scribbling = True

    def keyReleaseEvent(self, event):
        """Reimplemented from QGraphicsObject. Check if scribble key is released, toggling off scribbling mode.
        """
        if not event.isAutoRepeat():
            if event.key() == SCRIBBLE_KEY and self.scribbling:
                self.scribbling = False

    # Defining the length to be drawn as a Property
    @Property(float)
    def length(self):
        """float: The length of the grid lines to be drawn.
        When set, the grid lines points are set.
        """
        return self._length

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
    """The number ring which consists of the ringButtons for player input.

    Attributes
    ----------
    loseFocus : Signal
        An explicit signal for when the ring loses focus.
    keyPressed : Signal(str, bool)
        Emit when a digit is pressed, and whether scribbling mode is on
    """
    loseFocus = Signal()
    keyPressed = Signal(str, bool)

    def __init__(self, parent=None):
        """Create the ring buttons and layout. The parent argument is passed into BaseSudokuItem init method.
        """
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
        """When the animation is finished, hide away and freeze the buttons and loses the focus if it closes, or
        unfreeze it and set the transparency depending on mouse position if it opens"""
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

    def toggle_anim(self, toggling):
        """Toggle the animation to be play forward or backward
        """
        self.freeze_buttons(True)
        if toggling:
            self.anim.setDirection(QAbstractAnimation.Forward)
        else:
            self.anim.setDirection(QAbstractAnimation.Backward)

        self.anim.start()

    def boundingRect(self):
        """Reimplemented from QGraphicsObject
        """
        return QRectF(-5-self.radius-self.cell_width/2, -5-self.radius-self.cell_height/2,
                      self.cell_width+self.radius*2+10, self.cell_height + self.radius * 2 + 10)

    def paint(self, painter, style, widget=None):
        """Reimplemented from QGraphicsObject. Does nothing but is needed. May be used for fancy effects?
        """
        pass

    def send_button_press(self, val, btn):
        """Emits the keyPressed signal if any of the buttons is pressed, and attempts to close the ring

        Parameters
        ----------
        val : str
            The digit to be emitted
        """
        scribble = btn == 2
        self.keyPressed.emit(val, scribble)
        if not scribble:
            self.close_menu()
            
    def freeze_buttons(self, freeze):
        """Freezes the button

        Parameters
        ----------
        freeze: bool
            If true, freezes the button. Unfreezes otherwise.
        """
        for btn in self.cell_buttons:
            btn.set_freeze(freeze)

    def focusOutEvent(self, event):
        """Reimplemented from QGraphicsObject. Checks whether the mouse if over any of the buttons and refocus of so.
        This is here because clicking the button can cause the ring to focus out for some reason.
        """
        if not any(btn.isUnderMouse() for btn in self.cell_buttons):
            self.toggle_anim(False)
        else:
            self.setFocus()

    def mousePressEvent(self, event):
        """Reimplemented from QGraphicsObject. Similar reason to reimplementing focusOutEvent.
        """
        if not any(btn.isUnderMouse() for btn in self.cell_buttons):
            self.toggle_anim(False)
        else:
            self.setFocus()

    def close_menu(self):
        """Closes the ring if scribbling mode is off.
        """
        if not self.scribbling:
            self.toggle_anim(False)

    def keyPressEvent(self, event):
        """Reimplemented from QGraphicsObject.Get the digit pressed and emits the keyPressed signal.
        Check also if scribbling mode is on
        """
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
        """Reimplemented from QGraphicsObject. Toggle off scribbling mode if the scribble key is released.
        """
        if not event.isAutoRepeat():
            if event.key() == SCRIBBLE_KEY and self.scribbling:
                self.scribbling = False

    def hoverEnterEvent(self, event):
        """Reimplemented from QGraphicsObject. Make the ring opaque when the mouse enters the ring
        """
        self.set_buttons_transparent(False)

    def hoverLeaveEvent(self, event):
        """Reimplemented from QGraphicsObject. Make the ring transparent when the mouse enters the ring
        """
        self.set_buttons_transparent(True)

    def set_buttons_transparent(self, state):
        """Set the ring buttons transparent or opaque

        Parameters
        ----------
        state: bool
            If true, set the ring transparent, opaque otherwise.
        """
        for btn in self.cell_buttons:
            btn.set_transparent(state)

    # Defining the length to be drawn as a Property
    @Property(float)
    def radius(self):
        """float: The radius of the ring.
        When set, the buttons' position are set.
        """
        return self._radius

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
    """The menu which displays the difficulies before starting a game.

    Attributes
    ----------
    buttonClicked : Signal(str)

    """
    buttonClicked = Signal(str)

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
