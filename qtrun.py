# -*- coding: utf-8 -*-
# external imports
import sys
import threading
import time
from os.path import join

# PyQt5
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QDesktopWidget, QDialog, QAction, qApp

# internal imports
from qtictac import TicTacWidget, ICONS_PATH

# constants
MAIN_WINDOW_ICON_PATH = join(ICONS_PATH, 'tttoe_ico.png')

class QTicTacToe(QMainWindow):
    """
    Simple Qt GUI Main Window
    """
    def __init__(self):
        super(QTicTacToe, self).__init__()
        self.initUI()


    def initUI(self):
        # Thin user interface
        self.setWindowTitle('Tic Tac Toe')
        self.setWindowIcon(QIcon(MAIN_WINDOW_ICON_PATH))

        # Actions
        # exit
        exitAction = QAction(QIcon(join('ico', 'exit.png')), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
        # new game on a 3x3 game board
        newgame33Action = QAction(QIcon(join('ico', 'new.png')), '&New 3x3', self)
        newgame33Action.setShortcut('Ctrl+N')
        newgame33Action.setStatusTip('3x3')
        newgame33Action.triggered.connect(self.new_game(3, 3))
        # new game on a 3x4 game board (BONUS)
        newgame34Action = QAction(QIcon(join('ico', 'new_3x4.png')), '&New 3x4', self)
        newgame34Action.setShortcut('Ctrl+B')
        newgame34Action.setStatusTip('3x4')
        newgame34Action.triggered.connect(self.new_game(3, 4))
        # Simple menubar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        ticMenu = menubar.addMenu('&New')
        ticMenu.addAction(newgame33Action)
        ticMenu.addAction(newgame34Action)
        # Simple toolbar
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(newgame33Action)
        self.toolbar.addAction(newgame34Action)

        self.statusBar().showMessage('')
        self.setGeometry(300, 300, 300, 300)
        self.center()

        self.show()

    def new_game(self, h, w):
        def ng_callback():
            # function for making new gameboard with some fixed height(h) and width(w)
            if hasattr(self, 'tictactoe_widget'):
                # closing gameloop thread before substituting 'tictactoe_widget'
                if self.tictactoe_widget.gameloop.isRunning():
                    self.tictactoe_widget.gameloop.terminate()
            self.tictactoe_widget = TicTacWidget(self, h, w)
            self.setCentralWidget(self.tictactoe_widget)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QTicTacToe()
    sys.exit(app.exec_())
