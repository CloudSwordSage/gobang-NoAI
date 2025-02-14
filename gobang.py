# -*- coding: utf-8 -*-
# @Time    : 2025/2/14 14:14:49
# @Author  : 墨烟行(GitHub UserName: CloudSwordSage)
# @File    : gobang.py
# @Desc    : 基于 QT6 的 GUI 界面


from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPen
import copy
import sys
from game import Game
from minimax import MiniMax

class GobangWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.board = Game()
        self.ai = None
        self.cell_size = 40
        self.ai_player = 0
        self.setMouseTracking(True)
        self.hover_pos = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('五子棋 - PyQt6')
        self.setFixedSize(self.board.config.size * self.cell_size + 40,
                          self.board.config.size * self.cell_size + 120)

        self.canvas = QWidget(self)
        self.canvas.setMouseTracking(True)
        self.canvas.resize(self.board.config.size * self.cell_size + 40,
                           self.board.config.size * self.cell_size + 40)

        control_panel = QWidget(self)
        control_layout = QHBoxLayout()

        self.btn_ai_first = QPushButton('AI先手')
        self.btn_human_first = QPushButton('玩家先手')
        self.btn_restart = QPushButton('重新开始')

        self.btn_ai_first.clicked.connect(lambda: self.start_game(ai_first=True))
        self.btn_human_first.clicked.connect(lambda: self.start_game(ai_first=False))
        self.btn_restart.clicked.connect(self.reset_game)

        control_layout.addWidget(self.btn_ai_first)
        control_layout.addWidget(self.btn_human_first)
        control_layout.addWidget(self.btn_restart)
        control_panel.setLayout(control_layout)
        control_panel.setGeometry(20, self.height() - 80, self.width() - 40, 60)

        self.show()

    def start_game(self, ai_first=False):
        self.ai_player = 1 if ai_first else 2
        self.board.reset()
        self.ai = MiniMax(max_depth=2)
        if ai_first:
            self.ai_move()

    def reset_game(self):
        self.board.reset()
        self.ai = None
        self.update()

    def ai_move(self):
        if self.ai and self.board.current_player == self.ai_player:
            move = self.ai.search(copy.deepcopy(self.board))
            self.board.move(*move)
            self.update()
            done, winner = self.board.game_end()
            if done and (winner == self.ai_player):
                QMessageBox.information(self, '游戏结束', 'AI获胜!')
                self.reset_game()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        for i in range(self.board.config.size):
            x = 20 + i * self.cell_size
            painter.drawLine(20, x, 20 + (self.board.config.size - 1) * self.cell_size, x)
            painter.drawLine(x, 20, x, 20 + (self.board.config.size - 1) * self.cell_size)

        for i in range(self.board.config.size):
            for j in range(self.board.config.size):
                if self.board.board[i][j] != 0:
                    color = QColor(Qt.GlobalColor.black) if self.board.board[i][j] == 1 else QColor(Qt.GlobalColor.white)
                    painter.setBrush(color)
                    painter.drawEllipse(20 + i * self.cell_size - 15,
                                         20 + j * self.cell_size - 15, 30, 30)

        if self.hover_pos:
            x, y = self.hover_pos
            painter.setPen(QPen(Qt.GlobalColor.green, 2))
            painter.setBrush(QColor(0, 255, 0, 0))
            painter.drawRect(x * self.cell_size - 1, y * self.cell_size - 1,
                             self.cell_size + 1, self.cell_size + 1)

    def mousePressEvent(self, event):
        if not self.ai:
            return

        x = (event.pos().x()) // self.cell_size
        y = (event.pos().y()) // self.cell_size
        if 0 <= x < self.board.config.size and 0 <= y < self.board.config.size:
            self.board.move(x, y)
            self.update()
            done, winner = self.board.game_end()
            if done and (winner == 3 - self.ai_player):
                QMessageBox.information(self, '游戏结束', '玩家获胜!')
                self.reset_game()
            else:
                self.ai_move()

    def mouseMoveEvent(self, event):
        x = (event.pos().x()) // self.cell_size
        y = (event.pos().y()) // self.cell_size
        if 0 <= x < self.board.config.size and 0 <= y < self.board.config.size:
            self.hover_pos = (x, y)
        else:
            self.hover_pos = None
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GobangWindow()
    sys.exit(app.exec())
