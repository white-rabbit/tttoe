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
# icons
MAIN_WINDOW_ICON_PATH = join(ICONS_PATH, 'tttoe_ico.png')
EXIT_ICON_PATH = join('ico', 'exit.png')
NEW_3x3_ICON_PATH = join('ico', 'new.png')
NEW_3x4_ICON_PATH = join('ico', 'new_3x4.png')


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
        exit_action = QAction(QIcon(EXIT_ICON_PATH), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(qApp.quit)
        # new game on a 3x3 game board
        new_3x3_action = QAction(QIcon(NEW_3x3_ICON_PATH), '&New 3x3', self)
        new_3x3_action.setShortcut('Ctrl+N')
        new_3x3_action.setStatusTip('3x3')
        new_3x3_action.triggered.connect(self.new_game(3, 3))
        # new game on a 3x4 game board (BONUS)
        new_3x4_action = QAction(QIcon(NEW_3x4_ICON_PATH), '&New 3x4', self)
        new_3x4_action.setShortcut('Ctrl+B')
        new_3x4_action.setStatusTip('3x4')
        new_3x4_action.triggered.connect(self.new_game(3, 4))
        # Simple menubar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)
        new_menu = menubar.addMenu('&New')
        new_menu.addAction(new_3x3_action)
        new_menu.addAction(new_3x4_action)
        # Simple toolbar
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exit_action)
        self.toolbar.addAction(new_3x3_action)
        self.toolbar.addAction(new_3x4_action)

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
