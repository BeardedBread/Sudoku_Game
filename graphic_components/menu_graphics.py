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
        #print(self.size().width())
        painter.setPen(self.box_pen)
        painter.drawRect(box)
        painter.drawText(box, Qt.AlignCenter, "00:00")


class DifficultyDisplayer(QGraphicsWidget):
    notFocus = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)

        self.width = 100
        self.height = 50

        self.box_pen = QPen()
        self.box_pen.setColor(Qt.white)
        self.pen_width = 3
        self.box_pen.setWidth(self.pen_width)


        self.diff_box = QRectF(0, 0, self.width, self.height)
        self.diff_buttons = []
        self.difficulty = ['Easy', 'Normal', 'Hard', 'Insane']
        for i in range(4):
            btn = buttons.animBox(0, -(self.height + 10) * (i + 1),
                            self.width, self.height, self.difficulty[i], parent=self)
            btn.setVisible(False)
            self.diff_buttons.append(btn)

        self.setMinimumSize(QSizeF(self.width, self.height))
        self.setMaximumSize(QSizeF(self.width, self.height))

        self.size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.size_policy.setHeightForWidth(True)
        self.setSizePolicy(self.size_policy)

        self.selected = False
        self.focus_changed = False
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

    def paint(self, painter, style, widget=None):
        painter.setPen(self.box_pen)
        painter.drawRect(self.diff_box)
        painter.drawText(self.diff_box, Qt.AlignCenter, "Normal")
        #painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        #if not self.focus_changed:
        print('Click')
        if not self.selected:
            self.selected = True
            for btn in self.diff_buttons:
                btn.setVisible(self.selected)
            self.update()
            self.setFocus()
            #    self.focus_changed = False

    def boundingRect(self):
        if self.selected:
            return QRectF(-10, -(self.height+10)*4 -10, self.width+20, (self.height+10) * 4+5)
        else:
            return super().boundingRect()

    def focusOutEvent(self, event):
        print("diff focus out")
        self.selected = False
        #self.focus_changed = True
        #for btn in self.diff_buttons:
        #    btn.setVisible(False)

        self.notFocus.emit()

    def connect_buttons_signal(self, func):
        print('Diff buttons connected')
        for btn in self.diff_buttons:
            btn.buttonClicked.connect(func)
