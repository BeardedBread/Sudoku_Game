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
        self.gameboard = board.BoxBoard(400, 400)
        self.menuboard = board.BoxBoard(400, 50)
        self.gamegrid = board.SudokuGrid(450, 450)
        self.numring = board.NumberRing()

        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout.addItem(self.gameboard)
        self.layout.addItem(self.menuboard)
        self.form = QGraphicsWidget()
        self.form.setLayout(self.layout)
        #self.layout.addItem(self.gamegrid)
        #self.button1 = buttons.animBox(0, 0, 20, 20, 'a')
        #self.scene.addItem(self.button1)


        #self.scene.addItem(self.gameboard)
        self.scene.addItem(self.form)
        self.scene.addItem(self.gamegrid)
        self.scene.addItem(self.numring)
        self.setBackgroundBrush(QBrush(Qt.black))
        self.setRenderHint(QPainter.Antialiasing)
        self.setGeometry(0, 0, 600, 600)

        self.gamegrid.buttonClicked.connect(self.show_number_ring)
        self.numring.connect_button_signals(self.select_ring_number)

        self.ensureVisible(self.scene.sceneRect(), 50, 50)
        self.fitInView(self.gameboard.boundingRect(), Qt.KeepAspectRatio)
        self.show()

    def show_number_ring(self, x=0, y=0):
        if not self.gamegrid.selected:
            self.numring.setPos(x, y)
            self.numring.setVisible(True)
            self.gamegrid.selected = True
        else:
            self.numring.setVisible(False)
            self.gamegrid.selected = False

    def select_ring_number(self, val):
        if val == 'X':
            val = 0
        self.gamegrid.replace_cell_number(int(val))
        self.show_number_ring()


if __name__ == "__main__":
    app = 0
    app = QApplication(sys.argv)

    ex = SudokuWindow()

    sys.exit(app.exec_())