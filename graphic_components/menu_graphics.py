from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsWidget, QGraphicsItem,
                             QGraphicsLineItem, QGraphicsRectItem, QGraphicsObject,
                             QGraphicsItemGroup, QGraphicsLayoutItem)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal, QSizeF)


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
        #self.setGeometry(self.timer_box)
        #print(self.geometry().width())

    def paint(self, painter, style, widget=None):
        box = self.geometry()
        #print(self.size().width())
        painter.setPen(self.box_pen)
        painter.drawRect(box)
        painter.drawText(box, Qt.AlignCenter, "00:00")

    def boundingRect(self):
        return QRectF(QPointF(0, 0), self.geometry().size())

    def sizeHint(self, which, constraint=None):
        return QSizeF(self.width, self.height)
        #print(self.geometry().size().width(), self.geometry().size().height())
        #return self.geometry().size()

    def setGeometry(self, rect):
        self.prepareGeometryChange()
        QGraphicsLayoutItem.setGeometry(self, rect)
        self.setPos(rect.topLeft())
