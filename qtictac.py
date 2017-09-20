# -*- coding: utf-8 -*-

# external imports
from os.path import join

# PyQt5
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout

from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtCore import QThread


# internal imports
from core.tictac import TicTacToe
from core.gameboard import GameBoard
from core.player import Player, AI
from core.utils import add


# constants
ICONS_PATH = 'ico'
X_ICON_PATH = join(ICONS_PATH, 'cross.png')
O_ICON_PATH = join(ICONS_PATH, 'smile.png')
E_ICON_PATH = join(ICONS_PATH, 'empty.png')


class ChoosePlayerDialog(QDialog):
    def __init__(self, parent=None):
        super(ChoosePlayerDialog, self).__init__(parent)
        self.first_player = False

        lbl_choose = QLabel('Choose player: ')
        btn_first_player = QPushButton('', self)
        btn_first_player.setFixedSize(QSize(70, 70))
        btn_first_player.setIconSize(QSize(60, 60))
        btn_first_player.setIcon(QIcon(join(X_ICON_PATH)))
        

        btn_second_player = QPushButton('', self)
        btn_second_player.setFixedSize(QSize(70, 70))
        btn_second_player.setIconSize(QSize(60, 60))
        btn_second_player.setIcon(QIcon(O_ICON_PATH))

        btn_first_player.clicked.connect(self.choose())
        btn_second_player.clicked.connect(self.choose(first_player_chosen = False))

        hlayout = QHBoxLayout()
        hlayout.addWidget(btn_first_player)
        hlayout.addWidget(btn_second_player)

        vlayout = QVBoxLayout(self)
        vlayout.addWidget(lbl_choose)
        vlayout.addLayout(hlayout)

        self.setWindowTitle('New game')


    def choose(self, first_player_chosen = True):
        def callback():
            self.first_player = first_player_chosen
            self.accept()
        return callback


class TicTacWidget(QWidget):
    # signal for game board updating
    update_board_signal = pyqtSignal()
    def __init__(self, parent, height, width):
        super(TicTacWidget, self).__init__(parent)

        game_board = GameBoard(height, width)
        user = Player(interface_callback = self.user_input)
        robot = AI()

        user_choise = ChoosePlayerDialog()
        user_choise.exec_()

        player_1, player_2 = (user, robot) if user_choise.first_player else (robot, user)
        self.tictac = TicTacToe(game_board, player_1, player_2, show_callback=self.update_board_signal.emit)
        self.update_board_signal.connect(self.update_game_status)

        # a bit overhead for user input organization
        self.user_input_wait_condition = QtCore.QWaitCondition()
        self.user_input_wait_mutex = QtCore.QMutex()
        self.user_input_data = None
        
        self.initBoard()

        self.game_loop()

        
    def game_loop(self):
        """
        Run a game loop in another thread.
        """
        class GameLoop(QThread):
            def __init__(self, parent, tictac):
                super(GameLoop, self).__init__(parent)
                self.tictac = tictac
            def run(self):
                self.tictac.play()

        self.gameloop = GameLoop(self, self.tictac)
        # Run in new thread
        self.gameloop.start()

    def initBoard(self):
        """
        Game board initializing.
        """
        # default game board state
        self.button_icons = {'X' : QIcon(X_ICON_PATH),
                             'O' : QIcon(O_ICON_PATH),
                             ' ' : QIcon(E_ICON_PATH)}
        self.button_size = 100 #px
        self.icon_size = 80 #px

        gb = self.tictac.game_board

        # a button grid
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        positions = [(i,j) for i in range(gb.height) for j in range(gb.width)]

        for position in positions:
            button = QPushButton('')
            button.setFixedSize(QSize(self.button_size, self.button_size))
            button.setIcon(self.get_button_icon(*position))
            button.setIconSize(QSize(self.icon_size, self.icon_size))
            button.clicked.connect(self.set_label(*position))
            self.grid.addWidget(button, *position)

    def get_button_icon(self, i, j):
        """
        Returns icon for button in position (i, j) on the game board.
        """
        label = self.tictac.game_board.label(i + 1, j + 1)
        return self.button_icons[label]

    def user_input(self, game_board):
        """
        User input callback. Waiting for button clicking.
        """
        self.user_input_wait_mutex.lock()
        self.user_input_wait_condition.wait(self.user_input_wait_mutex)
        self.user_input_wait_mutex.unlock()
        return self.user_input_data

    def update_game_status(self, game_over = False):
        """
        Calls after emitting signal for gameboard updating.
        """

        self.update_buttons_grid()

        gb = self.tictac.game_board
        current_status = gb.status()

        self.parent().statusBar().showMessage(current_status)
        
        if gb.game_over():
            enabled_positions = gb.winning_indicies()
            if enabled_positions:
                enabled_positions = set(reduce(add, enabled_positions))
            for i in xrange(gb.height):
                for j in xrange(gb.width):
                    item = self.grid.itemAtPosition(i, j)
                    button = item.widget()    
                    button.setEnabled((i + 1, j + 1) in enabled_positions)

    def update_buttons_grid(self):
        """
        Update buttons grid.
        """
        gb = self.tictac.game_board
        for i in xrange(gb.height):
            for j in xrange(gb.width):
                label = self.tictac.game_board.label(i + 1, j + 1)
                item = self.grid.itemAtPosition(i, j)
                button = item.widget()
                button.setEnabled(label == ' ')
                button.setIcon(self.get_button_icon(i, j))
                
    def set_label(self, *position):
        """
        Put label on some position.
        This function wakes up self.user_input function.
        After then gameloop is continued and emiting  signal for the game board updating...
        """
        def calluser():
            i, j = position
            self.user_input_data = i + 1, j + 1
            self.user_input_wait_condition.wakeAll()
        return calluser

   



