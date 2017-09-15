# -*- coding: utf-8 -*-

import sys
from os.path import join

from PyQt5.QtGui import QIcon, QFont


from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QToolTip, QPushButton, QMessageBox
from PyQt5.QtWidgets import QDesktopWidget, QFrame
from PyQt5.QtWidgets import QAction, qApp, QGridLayout

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QSize
from PyQt5.QtCore import QCoreApplication

from core.gameboard import GameBoard, STATUS
from core.player import Player, PLAYER_TYPE
class TicTacToe(QMainWindow):

    def __init__(self):
        super(TicTacToe, self).__init__()

        self.initUI()


    def initUI(self):
        exitAction = QAction(QIcon(join('ico', 'exit.png')), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        newgameAction = QAction(QIcon(join('ico', 'new.png')), '&New', self)
        newgameAction.setShortcut('Ctrl+N')
        newgameAction.setStatusTip('New game')
        newgameAction.triggered.connect(self.new_game)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(newgameAction)

        QToolTip.setFont(QFont('SansSerif', 10))
        self.setGeometry(300, 300, 300, 220)
        self.center()
        self.setWindowTitle('Tic Tac Toe')
        self.setWindowIcon(QIcon(join('ico', 'tttoe_ico.png')))

        self.setToolTip('Tic Tac Toe')

        self.tboard = Board(self, 3, 3)
        self.setCentralWidget(self.tboard)

        self.show()


    def new_game(self):
        self.tboard = Board(self, 4, 3)
        self.setCentralWidget(self.tboard)


    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message', 
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Board(QFrame):

    def __init__(self, parent, height, width):
        super(Board, self).__init__(parent)
        self.width = width
        self.height = height
        self.game_board = GameBoard(height, width)
        self.button_icons = {'X' : QIcon(join('ico', 'cross.png')),
                             'O' : QIcon(join('ico', 'smile.png')),
                             ' ' : QIcon(join('ico', 'empty.png'))}

        self.neo = Player(PLAYER_TYPE.AI)
        self.game_over = False
        self.initBoard()

    def get_button_icon(self, i, j):
        label = self.game_board.label(i + 1, j + 1)
        return self.button_icons[label]


    def update_game_status(self):
        current_status = self.game_board.status()
        self.parent().statusBar().showMessage(current_status)
        self.game_over = current_status != 'GAME'

        if self.game_over:
            enabled_positions = self.game_board.winning_indicies()
            if enabled_positions:
                add = lambda a, b : a + b
                enabled_positions = set(reduce(add, enabled_positions))
            for i in xrange(self.game_board.height):
                for j in xrange(self.game_board.width):
                    item = self.grid.itemAtPosition(i, j)
                    button = item.widget()
                    
                    button.setEnabled((i + 1, j + 1) in enabled_positions)

    def update_position(self, *position):

        if self.game_board.position_strength(self.game_board.position) == STATUS.WINNING:
            print 'winning for', self.game_board.player_label(self.game_board.position)
        elif self.game_board.position_strength(self.game_board.position) == STATUS.LOSING:
            print 'losing for', self.game_board.player_label(self.game_board.position)
        elif self.game_board.position_strength(self.game_board.position) == STATUS.DRAW:
            print 'draw for', self.game_board.player_label(self.game_board.position)

        i, j = position
        self.game_board.update_position(i + 1, j + 1)


        label = self.game_board.label(i + 1, j + 1)
        item = self.grid.itemAtPosition(i, j)
        button = item.widget()
        button.setEnabled(False)
        button.setIcon(self.get_button_icon(*position))

        self.update_game_status()
        

    def set_label(self, *position):
        def calluser():
            if not self.game_over: self.update_position(*position)
            if not self.game_over:
                next_position = self.neo.AI_next_position(self.game_board)
                path = self.neo.move_to(self.game_board, next_position)
                self.update_position(*path)
            

        return calluser

    def initBoard(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        positions = [(i,j) for i in range(self.height) for j in range(self.width)]

        for position in positions:
            button = QPushButton('')
            button.setFixedWidth(100)
            button.setFixedHeight(100)
            button.setIcon(self.get_button_icon(*position))
            button.setIconSize(QSize(80, 80))
            button.clicked.connect(self.set_label(*position))
            self.grid.addWidget(button, *position)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = TicTacToe()
    sys.exit(app.exec_())
    sys.exit(app.exec_())