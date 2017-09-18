# -*- coding: utf-8 -*-

import sys
import threading
import time
from os.path import join

from PyQt5.QtGui import QIcon, QFont


from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QToolTip, QPushButton, QMessageBox
from PyQt5.QtWidgets import QDesktopWidget, QFrame, QDialog, QHBoxLayout
from PyQt5.QtWidgets import QAction, qApp, QGridLayout, QDialogButtonBox

from PyQt5.QtCore import Qt, QBasicTimer, pyqtSignal, QSize
from PyQt5.QtCore import QCoreApplication

from core.tictac import TicTacToe
from core.gameboard import GameBoard
from core.player import Player, AI



class ChoosePlayerDialog(QDialog):
    def __init__(self, parent=None):
        super(ChoosePlayerDialog, self).__init__(parent)
        self.first_player = False

        self.buttonFirst = QPushButton('', self)
        self.buttonFirst.setFixedSize(QSize(70, 70))
        self.buttonFirst.setIconSize(QSize(60, 60))
        self.buttonFirst.setIcon(QIcon(join('ico', 'cross.png')))
        

        self.buttonSecond = QPushButton('', self)
        self.buttonSecond.setFixedSize(QSize(70, 70))
        self.buttonSecond.setIconSize(QSize(60, 60))
        self.buttonSecond.setIcon(QIcon(join('ico', 'smile.png')))

        self.buttonFirst.clicked.connect(self.choose())
        self.buttonSecond.clicked.connect(self.choose(first_player_chosen = False))

        self.setWindowTitle('Choose player')

        layout = QHBoxLayout(self)
        layout.addWidget(self.buttonFirst)
        layout.addWidget(self.buttonSecond)
        self.setToolTip('Choose Player')


    def choose(self, first_player_chosen = True):
        def callback():
            self.first_player = first_player_chosen
            self.accept()
        return callback
       

class QTicTacToe(QMainWindow):

    def __init__(self):
        super(QTicTacToe, self).__init__()

        self.initUI()


    def initUI(self):
        exitAction = QAction(QIcon(join('ico', 'exit.png')), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        newgame33Action = QAction(QIcon(join('ico', 'new.png')), '&New', self)
        newgame33Action.setShortcut('Ctrl+N')
        newgame33Action.setStatusTip('New 3x3 game')
        newgame33Action.triggered.connect(self.new_game(3, 3))

        newgame34Action = QAction(QIcon(join('ico', 'new_3x4.png')), '&New', self)
        newgame34Action.setShortcut('Ctrl+N+N')
        newgame34Action.setStatusTip('New 3x4 game')
        newgame34Action.triggered.connect(self.new_game(3,4))

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(newgame33Action)
        self.toolbar.addAction(newgame34Action)

        QToolTip.setFont(QFont('SansSerif', 10))
        self.setGeometry(300, 300, 300, 220)
        self.center()
        self.setWindowTitle('Tic Tac Toe')
        self.setWindowIcon(QIcon(join('ico', 'tttoe_ico.png')))

        self.setToolTip('Tic Tac Toe')

        self.show()


    def new_game(self, h, w):
        def ng_callback():
            self.tboard = Board(self, h, w)
            self.setCentralWidget(self.tboard)

        return ng_callback


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
        user_choise = ChoosePlayerDialog()
        user_choise.exec_()

        game_board = GameBoard(height, width)
        user = Player(interface_callback = self.user_move)
        robot = AI()

        player_1, player_2 = (user, robot) if user_choise.first_player else (robot, user)
        tictac = TicTacToe(game_board, player_1, player_2, show_callback=self.update_game_status)
        self.tictac = tictac

        self.button_icons = {'X' : QIcon(join('ico', 'cross.png')),
                             'O' : QIcon(join('ico', 'smile.png')),
                             ' ' : QIcon(join('ico', 'empty.png'))}

        self.initBoard()

        self.user_i, self.user_j = None, None
        self.game_loop()

    def game_loop(self):
        # Create the new thread. The target function is 'myThread'. The
        # function we created in the beginning.
        t = threading.Thread(name = 'TicTacLoop', target = self.tictac.play)
        t.start()

    def user_move(self, game_board):
        while True:
            if self.user_i is not None and self.user_j is not None:
                print self.user_i, self.user_j
                i, j = self.user_i, self.user_j
                self.user_i, self.user_j = None, None
                return i + 1, j + 1

            time.sleep(0.1)

    def get_button_icon(self, i, j):
        label = self.tictac.game_board.label(i + 1, j + 1)
        return self.button_icons[label]


    def update_game_status(self, game_over = False):
    
        self.update_buttons()

        gb = self.tictac.game_board
        current_status = gb.status()

        self.parent().statusBar().showMessage(current_status)
        
        if game_over:

            enabled_positions = gb.winning_indicies()
            if enabled_positions:
                add = lambda a, b : a + b
                enabled_positions = set(reduce(add, enabled_positions))
            for i in xrange(gb.height):
                for j in xrange(gb.width):
                    item = self.grid.itemAtPosition(i, j)
                    button = item.widget()
                    
                    button.setEnabled((i + 1, j + 1) in enabled_positions)

    def update_buttons(self):
        gb = self.tictac.game_board
        for i in xrange(gb.height):
            for j in xrange(gb.width):
                label = self.tictac.game_board.label(i + 1, j + 1)
                item = self.grid.itemAtPosition(i, j)
                button = item.widget()
                if label != ' ':
                    button.setEnabled(False)
                button.setIcon(self.get_button_icon(i, j))
                
        

    def set_label(self, *position):
        def calluser():
            self.user_i, self.user_j = position
        return calluser

    def initBoard(self):

        gb = self.tictac.game_board
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        positions = [(i,j) for i in range(gb.height) for j in range(gb.width)]

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
    ex = QTicTacToe()
    sys.exit(app.exec_())
    sys.exit(app.exec_())