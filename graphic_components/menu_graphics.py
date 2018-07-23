"""
This module contains the components that make up the menu Board
"""

import sys

from PyQt5.Qt import QApplication
from PyQt5.QtCore import (Qt, QRectF, pyqtSignal, QSizeF, QTimer)
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtWidgets import (QSizePolicy, QGraphicsWidget, QGraphicsItem,
                             QGraphicsObject, QGraphicsProxyWidget,
                             QGraphicsScene, QGraphicsView, )
from general.highscore import DIFFICULTIES

if __name__ == "__main__":
    import buttons
    import scoreboard as scb
else:
    from . import buttons
    from . import scoreboard as scb



class TimerDisplayer(QGraphicsWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        #self.setParent(parent)
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
        self.timer.timeout.connect(self.increase_time)
        self.timer.start()

    def increase_time(self):
        self.atenth_seconds += 1
        self.update()

    def reset_time(self):
        self.atenth_seconds = 0
        self.timer.start()

    def get_time(self):
        return "{:02d}:{:02d}:{:1d}".format(int(self.atenth_seconds/600),
                                            int(self.atenth_seconds/10) % 60,
                                            self.atenth_seconds % 10)

    def paint(self, painter, style, widget=None):
        box = self.timer_box
        painter.setPen(self.box_pen)
        painter.drawRect(box)
        painter.drawText(box, Qt.AlignCenter,
                         "{:02d}:{:02d}:{:1d}".format(int(self.atenth_seconds/600),
                                                      int(self.atenth_seconds/10) % 60,
                                                      self.atenth_seconds % 10))


class DifficultyDisplayer(QGraphicsWidget):
    notFocus = pyqtSignal()
    difficultySelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.width = 100
        self.height = 50

        self.diff_menu = DifficultyMenu(self.width, self.height, self)
        self.diff_menu.setY(-self.diff_menu.height)
        self.diff_menu.setVisible(False)

        self.text = "None"

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
        if state:
            self.setAcceptedMouseButtons(Qt.NoButton)
        else:
            self.setAcceptedMouseButtons(Qt.LeftButton)

    def paint(self, painter, style, widget=None):
        painter.setPen(self.box_pen)
        painter.drawRect(self.diff_box)
        painter.drawText(self.diff_box, Qt.AlignCenter, self.text)
        painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        if not self.diff_menu.isVisible():
            self.diff_menu.setFocus()
            self.diff_menu.setVisible(True)
        else:
            self.diff_menu.setVisible(False)
            self.notFocus.emit()

    def selected_difficulty(self, string):
        self.diff_menu.setVisible(False)
        self.set_text(string)
        self.notFocus.emit()

    def set_text(self, string):
        self.text = string
        self.update()

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)


class DifficultyMenu(QGraphicsWidget):

    menuClicked = pyqtSignal(str)
    loseFocus = pyqtSignal()

    def __init__(self, width, height, parent=None):
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
        return QRectF(0, 0, self.width, self.height)

    def clicked_on(self, string):
        self.menuClicked.emit(string)

    def focusOutEvent(self, event):
        if not any(btn.isUnderMouse() for btn in self.diff_buttons) and not self.parent().isUnderMouse():
            self.loseFocus.emit()
            self.setVisible(False)


class HighScoreDisplayer(QGraphicsObject):

    def __init__(self, parent=None):
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
        return QRectF(-self.size, -self.size, self.size, self.size)

    def paint(self, painter, style, widget=None):
        painter.setPen(self.box_pen)
        painter.drawRect(self.boundingRect())
        if not self.selected:
            painter.fillRect(-self.icon_size/4, -self.icon_size/4,
                             -self.icon_size/2, -self.icon_size/2, Qt.white)

    def hoverEnterEvent(self, ev):
        self.show_board(True)

    def hoverLeaveEvent(self, ev):
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
