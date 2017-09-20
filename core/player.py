# external imports:
from random import randint

# internal imports:
from utils import die, enum, add, count_of
from gameboard import GameBoard, GameBoardException, STATUS


MAX_SEARCHING_DEPTH = 5

class PlayerException(Exception):
    def __init__(self, message):
        super(PlayerException, self).__init__(message)

class Player(object):
    def __init__(self, interface_callback = None):
        """
        Player construction.

        Parameters
        ----------
        inteface_callback(callable): is a function or class method that returns coordinates for player move.
        """
        self.__next_position = interface_callback if (interface_callback is not None) else self.__console_input

    def __console_input(self, game_board):
        """
        Default console input.
        """
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
        game_board (GameBoard): current state of game board.
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
        """
        The next position by AI.
        Returns
        ---------
        (int, int) a tuple of coordinates.
        """
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
        """
        This function for choosing move when current position is losing.
        
        Parameters
        ----------
        gameboard (GameBoard): current state of the game board.
        available_positions (dict): available positions combined by their strength value.

        Retruns
        ---------- 
        (int, int) coordinates of move (the first value from 1 to board.height, the second value from 1 to board.width)
        """
        max_depth = 0
        best_pos = None

        for pos in available_positions[STATUS.WINNING]:
            cur_depth = 1 + self.__shortest_game_steps(gameboard, pos, 1)
            if cur_depth > max_depth:
                best_pos = pos
                max_depth = cur_depth
        return best_pos

    def __shortest_game_steps(self, gameboard, pos, cur_depth):
        """
        The current player wants to minimize game steps from position pos.
        """
        if cur_depth == MAX_SEARCHING_DEPTH: return 0
        avpos = gameboard.available_positions(pos)
        lf_count = count_of(avpos, STATUS.LOSING_FINAL)
        if lf_count > 0:
            # this trick for minimization the enemy winning positions
            return 1 if lf_count == 1 else 0 
        else:
            min_rec_depth = 1e9
            for next_pos in avpos[STATUS.LOSING]:
                min_rec_depth = min(min_rec_depth, 1 + self.__longest_game_steps(gameboard, next_pos, cur_depth + 1))
            return min_rec_depth


    def __longest_game_steps(self, gameboard, pos, cur_depth):
        """
        The current player wants to maximize game staps from position pos.
        The position 'pos' is actually losing for current player!!
        """
        if cur_depth == MAX_SEARCHING_DEPTH: return 0
        avpos = gameboard.available_positions(pos)
        max_rec_depth = 0
        for next_pos in avpos[STATUS.WINNING]:
            max_rec_depth = max(max_rec_depth, 1 + self.__shortest_game_steps(gameboard, next_pos, cur_depth + 1))
        return max_rec_depth


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
    player_2 = AI()
    player_2.move(gb)
    player_2.move(gb)

    print gb.position


if __name__ == '__main__':
    main()