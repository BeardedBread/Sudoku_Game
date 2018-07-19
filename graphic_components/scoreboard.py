from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt5.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QGridLayout, QVBoxLayout,
                             QPushButton, QLabel)
from PyQt5.QtCore import (QAbstractAnimation, QObject, QPointF, Qt, QRectF, QLineF,
                          QPropertyAnimation, pyqtProperty, pyqtSignal, QSizeF, QTimer)
from PyQt5.Qt import QApplication
import sys

class HighScoreBoard(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.addLayout(DifficultySwitch())
        self.layout.addLayout(ScoreGrid())
        self.layout.addWidget(NameInput())


class DifficultySwitch(QHBoxLayout):

    def __init__(self):
        super().__init__()

        left_btn = QPushButton('<')
        difficulty_display = QLabel('Normal')
        right_btn = QPushButton('>')

        self.addWidget(left_btn)
        self.addWidget(difficulty_display)
        self.addWidget(right_btn)


class ScoreGrid(QGridLayout):

    def __init__(self):
        super().__init__()

        for i in range(5):
            label = QLabel(str(i)+'.')
            self.addWidget(label, i, 0)

        for i, name in enumerate('ABCDE'):
            label1 = QLabel(name)
            label2 = QLabel('0')
            self.addWidget(label1, i, 1)
            self.addWidget(label2, i, 2)


class NameInput(QWidget):

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)

        self.layout.addWidget(QLabel('Name'))

        self.name_input = QLineEdit(self)
        self.layout.addWidget(self.name_input)


if __name__ == '__main__':
    app = 0
    app = QApplication(sys.argv)

    ex = HighScoreBoard()
    ex.show()
    sys.exit(app.exec_())