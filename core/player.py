# external imports:
from random import randint

# internal imports:
from utils import die, enum, add
from gameboard import GameBoard, GameBoardException, STATUS


class PlayerException(Exception):
    def __init__(self, message):
        super(PlayerException, self).__init__(message)


class Player(object):
    def __init__(self, interface_callback = None):
        self.__next_position = interface_callback if (interface_callback is not None) else self.__console_input

    def __console_input(self, game_board):
        while True:
            try:
                i, j = [int(x) for x in raw_input("Enter coordinates: ").split()]
                return (i, j)
            except Exception:
                print('Wrong format, two integer values needed.')
        

        
    def move(self, game_board):
        """
        Changes game board by making the current player move.
        
        Parameters
        ----------
        game_board (GameBoard) current state of game board.
        """
        while True:
            try:
                i, j = self.__next_position(game_board)
                game_board.update_position(i, j)
                break
            except GameBoardException as GBE:
                print(GBE.message)
        

class AI(Player):
    def __init__(self):
        super(AI, self).__init__(self.__AI_move)


    def __AI_move(self, game_board):
        best_pos = self.__AI_next_position(game_board)
        return self.__move_to(game_board, best_pos)
        

    def __move_to(self, game_board, new_position):
        """
        Calculates the difference between game_board.position and new_position.game_board
        If there is some way from game_board.position to new position by one move
        the method returns corresponding coordinates.
        
        Parameters
        ----------
        game_board (GameBoard): current state of game board.
        new_position     (str): string mask of new position.

        Retruns
        ---------- 
        (int, int) coordinates of move (the first value from 1 to board.height, the second value from 1 to board.width)
        """
        index = -1
        from_position = game_board.position
        for i in xrange(len(from_position)):
            if from_position[i] != new_position[i]:
                if index == -1:
                    index = i
                else:
                    raise PlayerException('It is not possible to move from %s to %s.' % (from_position, new_position))
        if index != -1:
            return index / game_board.width + 1, index % game_board.width + 1


    def __dummy_prophet(self, gameboard, available_positions):
        strength = 0
        best = None
        goodness = 0
        positions = reduce(add, map(lambda x : available_positions[x], available_positions))
        for pos in positions:
            if best == None : best = pos
            avpos = gameboard.available_positions(pos)

            def count_of(strength_value):
                if strength_value in avpos:
                    return len(avpos[strength_value])
                else:
                    return 0
            if count_of(STATUS.LOSING_FINAL) == 0:
                best = pos
            
        return best


    def __AI_next_position(self, game_board):
        """
        The best way for the player which moved from the current position.

        Parameters
        ----------
        game_board  (GameBoard):      Current state of game board.
        
        Returns
        ----------
        (str) the next position of the game board including the current player move.
        """
        position = game_board.position       
        player_label = game_board.player_label(position)

        empty = filter(lambda pair : pair[1] == ' ', enumerate(position))
        empty_indexes = map(lambda pair : pair[0], empty)
        if len(empty_indexes) > 12:
            i = empty_indexes[randint(0, len(empty_indexes) - 1)]
            next_position = position[:i] + player_label + position[i + 1:]
            return next_position
        else:
            strength = game_board.position_strength(position)

            available_positions = game_board.available_positions(position)

            def random_mask(current_strength):
                count = len(available_positions[current_strength]) if current_strength in available_positions else 0
                if count > 0: 
                    random_index = randint(0, count - 1)
                    return available_positions[current_strength][random_index]

            ret = None
            if strength == STATUS.DRAW:
                ret = random_mask(STATUS.DRAW)
            elif strength == STATUS.WINNING or strength == STATUS.WINNING_FINAL:
                mask = random_mask(STATUS.LOSING)
                ret = mask if mask is not None else random_mask(STATUS.LOSING_FINAL)  
            elif strength == STATUS.LOSING or strength == STATUS.LOSING_FINAL:
                return self.__dummy_prophet(game_board, available_positions)
            else:
                raise PlayerException('Unknown statuses of available positions.')
            return ret

def main():
    gb = GameBoard(3, 3)
    player_1 = Player(PLAYER_TYPE.AI)
    player_2 = Player(PLAYER_TYPE.AI)

    for i in xrange(9):
        player_1.move(gb)
        print gb.position
        if gb.game_over():
            break
        player_2.move(gb)
        print gb.position
        if gb.game_over():
            break


if __name__ == '__main__':
    main()