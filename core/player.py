# external imports:
from random import randint

# internal imports:
from utils import die, enum
from gameboard import GameBoard, GameBoardException, STATUS


PLAYER_TYPE = enum('ALIVE', 'AI')

class Player(object):
    def __init__(self, player_type=PLAYER_TYPE.ALIVE):
        self.player_type = player_type

    def move(self, game_board):
        if self.player_type == PLAYER_TYPE.ALIVE:
            i, j = -1, -1
            while True:
                i, j = [int(x) for x in raw_input("Enter coordinates: ").split()]
                try:
                    game_board.update_position(i, j)
                    break
                except GameBoardException as GBE:
                    print GBE.message

        elif self.player_type == PLAYER_TYPE.AI:
            next_position = self.AI_next_position(game_board)
            i,j = self.move_to(game_board, next_position)
            game_board.update_position(i + 1, j + 1)
        else:
            raise PlayerException('Unknown type of player')

    def move_to(self, game_board, to_position):
        index = -1
        from_position = game_board.position
        for i in xrange(len(from_position)):
            if from_position[i] != to_position[i]:
                if index == -1:
                    index = i
                else:
                    raise PlayerException('It is not possible to move from %s to %s.' % (from_position, to_position))
        if index != -1:
            return index / game_board.board_width, index % game_board.board_width


    def AI_next_position(self, game_board):
        """
        The best way for the player which moved from the current position.

        Parameters
        ----------
        game_board  (GameBoard):      Current state of game board.
        
        Returns
        ----------
        (int) next state for the player or -1 if there is no moves from the current position.
        """
        position = game_board.position       
        player_label = game_board.player_label(position)

        empty = filter(lambda pair : pair[1] == ' ', enumerate(position))
        empty_indexes = map(lambda pair : pair[0], empty)
        if len(empty_indexes) > 12 or len(position) == len(empty):
            i = empty_indexes[randint(0, len(empty_indexes) - 1)]
            next_position = position[:i] + player_label + position[i + 1:]
            return next_position
        else:
            strength = game_board.position_strength(position)

            available_positions = game_board.available_positions(position)

            def random_mask(strength):
                count = len(available_positions[strength]) if strength in available_positions else 0
                if count > 0: 
                    random_index = randint(0, count - 1)
                    return available_positions[strength][random_index]

            ret = None
            if strength == STATUS.DRAW:
                ret = random_mask(STATUS.DRAW)
            elif strength == STATUS.WINNING or strength == STATUS.WINNING_FINAL:
                mask = random_mask(STATUS.LOSING)
                ret = mask if mask is not None else random_mask(STATUS.LOSING_FINAL)  
            elif strength == LOSING or strength == LOSING_FINAL:
                mask = random_mask(STATUS.WINNING)
                ret = mask if mask is not None else random_mask(STATUS.WINNING_FINAL)
            else:
                raise PlayerException('Unknown statuses of available positions.')
            return ret

def main():
    gb = GameBoard(3, 3)
    player_1 = Player(PLAYER_TYPE.AI)
    player_2 = Player(PLAYER_TYPE.ALIVE)

    for i in xrange(9):
        i, j = player_1.move(gb)
        gb.update_position(i, j)
        print gb.position
        if gb.game_over():
            break
        i, j = player_2.move(gb)
        gb.update_position(i, j)
        print gb.position
        if gb.game_over():
            break


if __name__ == '__main__':
    main()