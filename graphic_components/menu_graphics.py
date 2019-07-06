"""
This module contains the components that make up the menu Board
"""

import sys

from PySide2.QtCore import (Qt, QRectF, Signal, QSizeF, QTimer)
from PySide2.QtGui import QPainter, QBrush, QPen
from PySide2.QtWidgets import (QSizePolicy, QGraphicsWidget, QGraphicsItem, QGraphicsObject, QGraphicsProxyWidget, QGraphicsScene, QGraphicsView, QApplication)
from general.highscore import DIFFICULTIES

if __name__ == "__main__":
    import buttons
    import scoreboard as scb
else:
    from . import buttons
    from . import scoreboard as scb


class TimerDisplayer(QGraphicsWidget):
    """The widget to display the elapsed time. Unit of time is a tenth of a second.
    """
    def __init__(self, parent=None):
        """Set up the box to draw and the time string with the QTimer

        Parameters
        ----------
        parent: object
            Passed into QGraphicsWidget init method
        """
        super().__init__(parent=parent)
        self.width = 100
        self.height = 50

        self.box_pen = QPen()
        self.box_pen.setColor(Qt.white)
        self.pen_width = 3
        self.box_pen.setWidth(self.pen_width)

        self.timer_box = QRectF(0, 0, self.width, self.height)
        self.setMinimumSize(QSizeF(self.width, self.height))
        self.setMaximumSize(QSizeF(self.width, self.height))

        self.size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.size_policy.setHeightForWidth(True)
        self.setSizePolicy(self.size_policy)

        self.atenth_seconds = 0
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._increase_time)
        self.timer.start()

    def _increase_time(self):
        """Increase the time. Connected to the QTimer.
        """
        self.atenth_seconds += 1
        self.update()

    def reset_time(self):
        """Reset the time to 0 and start the QTimer
        """
        self.atenth_seconds = 0
        self.timer.start()

    def get_time(self):
        """Get the time formatted as such: (minutes):(seconds):(A tenth of a second)

        Returns
        -------
        str: the formatted time string
        """
        return "{:02d}:{:02d}:{:1d}".format(int(self.atenth_seconds/600),
                                            int(self.atenth_seconds/10) % 60,
                                            self.atenth_seconds % 10)

    def paint(self, painter, style, widget=None):
        """Reimplemented from QGraphicsWidget. Draw the box and the timer.
        """
        box = self.timer_box
        painter.setPen(self.box_pen)
        painter.drawRect(box)
        painter.drawText(box, Qt.AlignCenter, self.get_time())


class DifficultyDisplayer(QGraphicsWidget):
    """Display the current difficulty. Clicking on it displays the difficulty menu.

    Attributes
    ----------
    notFocus: pyqtSignal
        Emitted when it loses focus

    difficultySelected = pyqtSignal(str)
        Emitted when a difficulty is selected. Emits the selected difficulty
    """
    notFocus = Signal()
    difficultySelected = Signal(str)

    def __init__(self, parent=None):
        """Create the box and the text.

        Parameters
        ----------
        parent: object
            Passed into QGraphicsWidget init method
        """
        super().__init__(parent=parent)

        self.width = 100
        self.height = 50
        self.text = "None"

        self.diff_menu = DifficultyMenu(self.width, self.height, self)
        self.diff_menu.setY(-self.diff_menu.height)
        self.diff_menu.setVisible(False)

        self.box_pen = QPen()
        self.box_pen.setColor(Qt.white)
        self.pen_width = 3
        self.box_pen.setWidth(self.pen_width)

        self.diff_box = QRectF(0, 0, self.width, self.height)

        self.setMinimumSize(QSizeF(self.width, self.height))
        self.setMaximumSize(QSizeF(self.width, self.height))

        self.size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.size_policy.setHeightForWidth(True)
        self.setSizePolicy(self.size_policy)

        self.setAcceptedMouseButtons(Qt.LeftButton)

        self.diff_menu.menuClicked.connect(self.selected_difficulty)
        self.diff_menu.menuClicked.connect(self.difficultySelected.emit)
        self.diff_menu.loseFocus.connect(self.notFocus.emit)

    def set_disabled(self, state):
        """Set to disable mouse events.

        Parameters
        ----------
        state: bool
            True to disable, False otherwise
        """
        if state:
            self.setAcceptedMouseButtons(Qt.NoButton)
        else:
            self.setAcceptedMouseButtons(Qt.LeftButton)

    def paint(self, painter, style, widget=None):
        """Reimplemented from QGraphicsWidget. Draw the box and the difficulty text.
        """
        painter.setPen(self.box_pen)
        painter.drawRect(self.diff_box)
        painter.drawText(self.diff_box, Qt.AlignCenter, self.text)
        painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        """Reimplemented from QGraphicsWidget. Toggle the difficulty menu on click.
        """
        if not self.diff_menu.isVisible():
            self.diff_menu.setFocus()
            self.diff_menu.setVisible(True)
            self.clicked.emit()
        else:
            self.diff_menu.setVisible(False)
            self.notFocus.emit()

    def selected_difficulty(self, string):
        """Hide the difficulty menu once a difficulty is selected.

        Parameters
        ----------
        string: str
            The difficulty selected
        """
        self.diff_menu.setVisible(False)
        self.set_text(string)
        self.notFocus.emit()

    def set_text(self, string):
        """Set the text to be displayed. Should be one of the difficulty options.

        Parameters
        ----------
        string: str
            String to be set
        """
        self.text = string
        self.update()

    def boundingRect(self):
        """Reimplemented from QGraphicsWidget.
        """
        return QRectF(0, 0, self.width, self.height)


class DifficultyMenu(QGraphicsWidget):
    """The menu to select the difficulty.

    Attributes
    ----------
    menuClicked: pyqtSignal(str)
        Emitted when a difficulty is selected. Emits the difficulty string.

    loseFocus: pyqtSignal
        Emitted when the menu loses focus.
    """

    menuClicked = Signal(str)
    loseFocus = Signal()

    def __init__(self, width, height, parent=None):
        """Creates the five difficulty buttons

        Parameters
        ----------
        parent: object
            Passed into QGraphicsWidget init method
        """
        super().__init__(parent=parent)
        self.setParent(parent)

        self.diff_buttons = []
        self.btn_height = height
        self.btn_width = width
        self.height = (self.btn_height + 10) * 5
        self.width = self.btn_width

        for i in range(5):
            btn = buttons.MenuButton(0, (self.btn_height + 10) * i,
                                  self.btn_width, self.btn_height, DIFFICULTIES[i], parent=self)
            btn.buttonClicked.connect(self.clicked_on)
            self.diff_buttons.append(btn)

        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFocusPolicy(Qt.ClickFocus)

    def boundingRect(self):
        """Reimplemented from QGraphicsWidget.
        """
        return QRectF(0, 0, self.width, self.height)

    def clicked_on(self, string):
        """Emits the menuClicked signal with the selected difficulty, when one of the buttons is pressed.

        Parameters
        ----------
        string: The difficulty string from the buttons
        """
        self.menuClicked.emit(string)

    def focusOutEvent(self, event):
        """Reimplemented from QGraphicsWidget. Check that no buttons are pressed before losing focus.
        """
        if not any(btn.isUnderMouse() for btn in self.diff_buttons) and not self.parent().isUnderMouse():
            self.loseFocus.emit()
            self.setVisible(False)


class HighScoreDisplayer(QGraphicsObject):

    def __init__(self, parent=None):
        """Creates the five difficulty buttons

        Parameters
        ----------
        parent: object
            Passed into QGraphicsWidget init method
        """
        super().__init__(parent=parent)

        self.size = 25
        self.icon_size = 25
        self.board_size = 250

        self.box_pen = QPen()
        self.box_pen.setColor(Qt.white)
        self.pen_width = 3
        self.box_pen.setWidth(self.pen_width)

        self.widget_proxy = QGraphicsProxyWidget(parent=self)
        self.scoreboard_widget = scb.HighScoreBoard(self.board_size, self.board_size)
        self.widget_proxy.setWidget(self.scoreboard_widget)
        self.widget_proxy.setPos(-self.board_size, -self.board_size)
        self.scoreboard_widget.setVisible(False)

        self.setAcceptHoverEvents(True)
        self.selected = False

    def set_disabled(self, state):
        self.setAcceptHoverEvents(not state)

    def show_board(self, state):
        self.scoreboard_widget.setVisible(state)
        self.scoreboard_widget.show_scores(state)
        self.prepareGeometryChange()
        if state:
            self.size = self.board_size
        else:
            self.size = self.icon_size

    def boundingRect(self):
        """Reimplemented from QGraphicsWidget.
        """
        return QRectF(-self.size, -self.size, self.size, self.size)

    def paint(self, painter, style, widget=None):
        """Reimplemented from QGraphicsWidget. Paint the bounding rect as the border. Additionally,
        draw a white rectangle when not selected.
        """
        painter.setPen(self.box_pen)
        painter.drawRect(self.boundingRect())
        if not self.selected:
            painter.fillRect(-self.icon_size/4, -self.icon_size/4,
                             -self.icon_size/2, -self.icon_size/2, Qt.white)

    def hoverEnterEvent(self, ev):
        """Reimplemented from QGraphicsWidget. Show the score board.
        """
        self.show_board(True)

    def hoverLeaveEvent(self, ev):
        """Reimplemented from QGraphicsWidget. Hide the score board.
        """
        self.show_board(False)


if __name__ == "__main__":
    app = 0
    app = QApplication(sys.argv)

    # Set up the Scene to manage the GraphicItems
    view = QGraphicsView()
    scene = QGraphicsScene(0, 0, 500, 600)
    view.setScene(scene)
    view.setSceneRect(scene.sceneRect())

    # Add the Boards to the form with a vertical layout
    highscore = HighScoreDisplayer()
    highscore.setX(400)
    highscore.setY(400)
    scene.addItem(highscore)

    # Setting the view
    view.setBackgroundBrush(QBrush(Qt.black))
    view.setRenderHint(QPainter.Antialiasing)
    view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
    view.show()

    sys.exit(app.exec_())
