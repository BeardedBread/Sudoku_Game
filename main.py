from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont, QTransform, QWheelEvent
from PyQt5.Qt import QApplication, QTimer
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsView, QGraphicsItem,
                             QGraphicsLineItem, QGraphicsRectItem, QGraphicsObject,
                             QGraphicsItemGroup, QGraphicsWidget, QGraphicsLinearLayout)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPoint, QPointF, Qt, QRectF,QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal)
import sys

from graphic_components import board


class SudokuWindow(QGraphicsView):
    """
    The main window that shows the graphical components.
    Contains the Sudoku Board and the Menu Board.
    """

    def __init__(self):
        super().__init__()

        # Set up the Scene to manage the GraphicItems
        self.scene = QGraphicsScene(0, 0, 500, 600, self)
        self.setScene(self.scene)
        self.setSceneRect(self.scene.sceneRect())

        # Add the Boards to the form with a vertical layout
        self.form = QGraphicsWidget()
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.gameboard = board.GameBoard(400, 400)
        self.menuboard = board.MenuBoard(400, 80)
        self.layout.addItem(self.gameboard)
        self.layout.addItem(self.menuboard)
        self.layout.setSpacing(50)
        self.layout.setContentsMargins(50, 50, 50, 0)
        self.form.setLayout(self.layout)
        self.scene.addItem(self.form)

        # Setting the view
        self.setBackgroundBrush(QBrush(Qt.black))
        self.setRenderHint(QPainter.Antialiasing)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.show()

        # Cross-Board signal connections
        self.gameboard.gridDrawn.connect(lambda: self.menuboard.show_children(True))
        self.gameboard.newGameSelected.connect(self.menuboard.set_difficulty_text)
        self.gameboard.sudokuDone.connect(self.menuboard.stop_timer)
        self.menuboard.diff_display.notFocus.connect(self.gameboard.game_refocus)
        self.menuboard.diff_display.difficultySelected.connect(self.gameboard.new_game)

    def resizeEvent(self, event):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)


if __name__ == "__main__":
    app = 0
    app = QApplication(sys.argv)

    ex = SudokuWindow()
    sys.exit(app.exec_())
