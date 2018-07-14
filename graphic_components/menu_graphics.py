"""
This module contains the components that make up the menu Board
"""

from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import (QSizePolicy, QGraphicsWidget, QGraphicsItem,
                             QGraphicsLineItem, QGraphicsRectItem, QGraphicsObject,
                             QGraphicsItemGroup, QGraphicsLayoutItem)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal, QSizeF)

from . import buttons

DIFFICULTIES = ['Very Easy', 'Easy', 'Normal', 'Hard', 'Insane']

class TimerDisplayer(QGraphicsWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)
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

    def paint(self, painter, style, widget=None):
        box = self.timer_box
        painter.setPen(self.box_pen)
        painter.drawRect(box)
        painter.drawText(box, Qt.AlignCenter, "00:00")


class DifficultyDisplayer(QGraphicsWidget):
    notFocus = pyqtSignal()
    difficultySelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)

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
        self.setFocusPolicy(Qt.ClickFocus)

        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

        self.diff_menu.menuClicked.connect(self.selected_difficulty)
        self.diff_menu.menuClicked.connect(self.difficultySelected.emit)


    def paint(self, painter, style, widget=None):
        painter.setPen(self.box_pen)
        painter.drawRect(self.diff_box)
        painter.drawText(self.diff_box, Qt.AlignCenter, self.text)
        painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        print('Beep')
        if not self.diff_menu.isVisible():
            self.setFocus()
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

    def focusOutEvent(self, event):
        print('Menu lose focus')
        self.notFocus.emit()
        #self.diff_menu.setVisible(False)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)


class DifficultyMenu(QGraphicsWidget):

    menuClicked = pyqtSignal(str)

    def __init__(self, width, height, parent=None):
        super().__init__(parent=parent)

        self.diff_buttons = []
        self.btn_height = height
        self.btn_width = width
        self.height = (self.btn_height + 10) * 5
        self.width = self.btn_width

        for i in range(5):
            btn = buttons.animBox(0, (self.btn_height + 10) * i,
                                  self.btn_width, self.btn_height, DIFFICULTIES[i], parent=self)
            btn.buttonClicked.connect(self.clicked_on)
            self.diff_buttons.append(btn)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def clicked_on(self, string):
        self.menuClicked.emit(string)
