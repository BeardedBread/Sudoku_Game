from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import (QSizePolicy, QGraphicsWidget, QGraphicsItem,
                             QGraphicsLineItem, QGraphicsRectItem, QGraphicsObject,
                             QGraphicsItemGroup, QGraphicsLayoutItem)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal, QSizeF)

from graphic_components import buttons

class TimerDisplayer(QGraphicsWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

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
        super().__init__(parent)

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
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)

    def paint(self, painter, style, widget=None):
        painter.setPen(self.box_pen)
        painter.drawRect(self.diff_box)
        painter.drawText(self.diff_box, Qt.AlignCenter, "Normal")

    def mousePressEvent(self, event):
        self.selected = not self.selected
        for btn in self.diff_buttons:
            btn.setVisible(self.selected)
        self.update()
        if self.selected:
            self.setFocus()
        else:
            self.clearFocus()

    #def boundingRect(self):
    #    return QRectF(-20, -(self.height+10)*4 -20, self.width+40, (self.height+20) * 5)

    def focusOutEvent(self, event):
        self.selected = False
        for btn in self.diff_buttons:
            btn.setVisible(False)
        self.notFocus.emit()
