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
        self.scene = QGraphicsScene(0, 0, 420, 510, self)

        self.setScene(self.scene)
        self.setSceneRect(self.scene.sceneRect())
        self.gameboard = board.GameBoard(400, 400)
        self.menuboard = board.MenuBoard(400, 80)

        #self.gameboard = board.BoxBoard(400, 400)
        #self.menuboard = board.BoxBoard(400, 50)

        self.form = QGraphicsWidget()
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout.addItem(self.gameboard)
        self.layout.addItem(self.menuboard)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 0)
        self.form.setLayout(self.layout)

        self.scene.addItem(self.form)
        self.setBackgroundBrush(QBrush(Qt.black))
        self.setRenderHint(QPainter.Antialiasing)
        #self.setGeometry(self.scene.sceneRect().toRect())

        #self.ensureVisible(self.scene.sceneRect(), 50, 50)
        self.fitInView(self.form.boundingRect(), Qt.KeepAspectRatio)
        self.show()

        #self.menuboard.diff_display.diffClicked.connect(self.freeze_game)

    def freeze_game(self, freeze):
        self.menuboard.show_difficulty(freeze)
        self.gameboard.freeze_gameboard(freeze)



if __name__ == "__main__":
    app = 0
    app = QApplication(sys.argv)

    ex = SudokuWindow()
    sys.exit(app.exec_())