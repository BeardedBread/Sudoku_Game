from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.Qt import QApplication, QTimer
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsView, QGraphicsItem,
                             QGraphicsLineItem, QGraphicsRectItem, QGraphicsObject,
                             QGraphicsItemGroup, QGraphicsWidget, QGraphicsLinearLayout)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPoint, QPointF, Qt, QRectF,QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal)
import sys, math

from graphic_components import buttons, board


class SudokuWindow(QGraphicsView):

    def __init__(self):
        super().__init__()

        # Set up the Scene to manage the GraphicItems
        self.scene = QGraphicsScene(0, 0, 400, 500, self)

        self.setScene(self.scene)
        self.setSceneRect(self.scene.sceneRect())
        self.gameboard = board.GameBoard(400, 400)
        self.menuboard = board.MenuBoard(400, 80)

        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout.addItem(self.gameboard)
        self.layout.addItem(self.menuboard)
        self.form = QGraphicsWidget()
        self.form.setLayout(self.layout)

        self.scene.addItem(self.form)
        self.setBackgroundBrush(QBrush(Qt.black))
        self.setRenderHint(QPainter.Antialiasing)
        self.setGeometry(0, 0, 600, 600)

        self.ensureVisible(self.scene.sceneRect(), 10, 10)
        self.fitInView(self.gameboard.boundingRect(), Qt.KeepAspectRatio)
        self.show()


        print('menuboard')
        menubox = self.menuboard.geometry()
        print(menubox.left(), menubox.top())
        print(menubox.width(), menubox.height())

        print('menuboard')
        gamebox = self.gameboard.geometry()
        print(gamebox.left(), gamebox.top())
        print(gamebox.width(), gamebox.height())

if __name__ == "__main__":
    app = 0
    app = QApplication(sys.argv)

    ex = SudokuWindow()

    sys.exit(app.exec_())