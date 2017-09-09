from gameboard import GameBoard
from player import Player, PLAYER_TYPE


class TicTacToeException(Exception):
    def __init__(self, message):
        super(TicTacToeException, self).__init__(message)


class TicTacToe(object):
    def __init__(self, board, player1, player2):
        self.players = [player1, player2]
        self.game_board = board

    def text_play(self):
        player_index = 0
        self.show()
        while not self.game_board.game_over():
            self.players[player_index].move(self.game_board)
            player_index = (player_index + 1) % 2
            self.show()

        self.game_board.status()
                

    def show(self):
        """
        The text output for the current position.
        """
        gb = self.game_board
        print ' -----'
        for line_index in xrange(gb.board_height):
            print '|',
            print gb.position[line_index * gb.board_width: (line_index + 1) * gb.board_width],
            print '|'
        print ' -----'

def main():
    width, height = -1, -1
    bad = lambda x : x != 3 and x != 4
    while bad(width) or bad(height):
        height, width = [int(x) for x in raw_input("Enter height and width of game board: ").split()]

    gb = GameBoard(height, width)
    p1 = Player(PLAYER_TYPE.AI)
    p2 = Player(PLAYER_TYPE.ALIVE)
    ttoe = TicTacToe(gb, p1, p2)
    ttoe.text_play()

if __name__=='__main__':
    main()