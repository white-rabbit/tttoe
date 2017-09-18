from gameboard import GameBoard
from player import Player, AI, PlayerException
from utils import die

class TicTacToeException(Exception):
    def __init__(self, message):
        super(TicTacToeException, self).__init__(message)


class TicTacToe(object):
    def __init__(self, board, player1, player2, show_callback = None):
        self.players = [player1, player2]
        self.game_board = board
        self.show_info = show_callback if show_callback is not None else self.text_show

    def play(self):
        player_index = 0
        self.show_info()
        while not self.game_board.game_over():
            self.players[player_index].move(self.game_board)
            self.show_info()
            player_index = (player_index + 1) % 2

        self.show_info(game_over = True)

    def text_show(self, game_over = False):
        """
        The text output for the current position.
        """
        if not game_over:
            gb = self.game_board
            print(' -----')
            for line_index in xrange(gb.height):
                print '|',
                print gb.position[line_index * gb.width: (line_index + 1) * gb.width],
                print '|'
            print(' -----')
        else:
            print(self.game_board.status())


    def game_over(self):
        return self.game_board.game_over()


def main():
    width, height = -1, -1
    bad = lambda x : x != 3 and x != 4
    while bad(width) or bad(height):
        height, width = [int(x) for x in raw_input("Enter height and width of game board: ").split()]

    gb = GameBoard(height, width)
    p1 = Player()
    p2 = AI()
    ttoe = TicTacToe(gb, p1, p2)
    ttoe.play()

if __name__=='__main__':
    main()