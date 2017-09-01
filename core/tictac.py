# The tic-tac-toe game base class.

# external imports:
import numpy
from copy import deepcopy

# internal imports:
from utils import *
from ternary import POS_COUNT, E_IND, X_IND, O_IND
from ternary import decimal_to_mask, mask_to_decimal, canonical_representation, tttoe_representation
from bitop import bit_up, bit_down, is_up
from random import randint

# Strengths
UNKNOWN = -1
DEAD_HIT = 0
WINNING = 1
LOSING = 2
WINNING_FINAL = 3
LOSING_FINAL = 4
IMPOSSIBLE = 5

# Stencils of winning positions.
STENCILS  = [[0,1,2], [3,4,5], [6, 7, 8]] # 0) !!!|...|... 1) ...|!!!|... 2) ...|...|!!!
STENCILS += [[0,3,6], [1,4,7], [2, 5, 8]] # 3) !..|!..|!.. 4) .!.|.!.|.!. 5) ..!|..!|..!
STENCILS += [[0,4,8], [2,4,6]]            # 6) !..|!..|!.. 7) .!.|.!.|.!.
DEFAULT_STENCILS = 2**len(STENCILS) - 1

# Players.
X_PLAYER = 0
O_PLAYER = 1


class TicTacToeException(Exception):
    def __init__(self, message):
        super(TicTacToeException, self).__init__(message)

class TicTacToe(object):
    def __init__(self, start_pos):
        if isinstance(start_pos, str):
            start_pos = mask_to_decimal(start_pos)
        self.current_pos = start_pos
        # strength of all available positions
        # initially UNKNOWN
        self.pos_strength = numpy.zeros((2, POS_COUNT), numpy.int16) - 1

        
    
    def status(self, player_index, pos_index, prev_stencils_bmasks = None):
        """
        Obvious information about some position by using stencils.

        Parameters
        ----------
        player_index  (int):           Player index.
        pos_index  (int):              Position index.
        prev_stencils_bmasks (list):  
                                       A list of available stencils bitmasks for the first and the second player. Two integer values.
                                       For example a value [1, 128] is in binary notation [00000001, 10000000]
                                       means that the first player only may win by filling the first stencil
                                       and the second player only may win by filling the last stencil... 
                                       So, we can check only stencils corresponded to the up bits in binary notations of every player.

        Returns
        ----------
        (int) strength for current player
        (list) list of two integer values : bitmasks for the first and the second players after checking.
        """
        if prev_stencils_bmasks is None: prev_stencils_bmasks = [DEFAULT_STENCILS, DEFAULT_STENCILS]
        pos_mask = canonical_representation(decimal_to_mask(pos_index))

        # initial value of position strength for current player
        strength_for_current_player = UNKNOWN
        
        # Count of first and second players winning combination.
        # This list is used for IMPOSSIBLE positions detection. 
        wining_count = [0, 0]

        # Current bitmasks are at least like previous bitbasks.
        stencils_bmask = deepcopy(prev_stencils_bmasks)

        # common bitmask of first and second players
        common_bmask = stencils_bmask[0] | stencils_bmask[1]

        for i, stencil in enumerate(STENCILS):

            if is_up(common_bmask, i):

                label_count = [0,0,0]
                # The count of every kind labels calculation for the current stencil.
                for index in stencil:
                    label_count[int(pos_mask[index])] += 1

                if label_count[X_IND] != 0 and label_count[O_IND] != 0:
                    # 'X' and 'O' labels inside this stencil: 
                    # this stencil is not need anymore.
                    stencils_bmask[X_PLAYER] = bit_down(stencils_bmask[X_PLAYER], i)
                    stencils_bmask[O_PLAYER] = bit_down(stencils_bmask[O_PLAYER], i)                        
                elif label_count[X_IND] != 0:
                    # There is no 'O' labels inside this stencil:
                    # this stencil is not need for 'O' player.
                    stencils_bmask[O_PLAYER] = bit_down(stencils_bmask[O_PLAYER], i)
                    # if count of empty labels is zero - X player win.
                    if label_count[E_IND] == 0: wining_count[X_PLAYER] += 1
                elif label_count[O_IND] != 0:
                    # Similarly.
                    stencils_bmask[X_PLAYER] = bit_down(stencils_bmask[X_PLAYER], i)
                    if label_count[E_IND] == 0: wining_count[O_PLAYER] += 1


        if sum(wining_count) == 0:
            if sum(stencils_bmask) == 0:
                strength_for_current_player = DEAD_HIT
            else:
                strength_for_current_player = UNKNOWN
        elif sum(wining_count) == 1:
            if wining_count[player_index] == 1:
                strength_for_current_player = IMPOSSIBLE
            else:
                strength_for_current_player = LOSING_FINAL
        else:
            strength_for_current_player = IMPOSSIBLE

        return strength_for_current_player, stencils_bmask


    def available_moves(self, player_index, pos_index, stencils_bmasks = None):
        """
        List of avalable moves for the player which moved from current position.
        Parameters
        ----------
        player_index  (int):          Player index.
        pos_index  (int):             Position index.
        prev_stencils_bmasks (list):  A list of available stencils bitmasks for the first and the second player.        
        Returns
        ----------
        (dict) available moves - dictionary that collecting lists of masks for strength values. 
        """
        if stencils_bmasks is None: stencils_bmasks = [DEFAULT_STENCILS, DEFAULT_STENCILS]
        # Internal representation of current position.
        tttoe_mask = tttoe_representation(decimal_to_mask(pos_index))
        player_label = 'X' if player_index == X_PLAYER else 'O'
        enemy_index = (player_index + 1) % 2
        # Total count of moves
        moves = dict()

        for i in xrange(9):
            if tttoe_mask[i] == ' ':
                # A mask for the next move.
                tttoe_mask_next = tttoe_mask[:i] + player_label + tttoe_mask[i + 1:]
                # Recursion call for the next move.
                this_move_enemy_strength = self.calc_position_strength(enemy_index, mask_to_decimal(tttoe_mask_next), prev_stencils_bmasks = stencils_bmasks)
                if this_move_enemy_strength in moves:
                    moves[this_move_enemy_strength].append(tttoe_mask_next)
                else:
                    moves[this_move_enemy_strength] = [tttoe_mask_next]

        return moves

    def calc_position_strength(self, player_index, pos_index, prev_stencils_bmasks = None):
        """
        Position strength for the player which moved from current position.

        Parameters
        ----------
        player_index  (int):          Player index.
        pos_index  (int):             Position index.
        prev_stencils_bmasks (list):  A list of available stencils bitmasks for the first and the second player.        
        Returns
        ----------
        (int) position strength for current player.
        """
        # setting default value for both stencils
        if prev_stencils_bmasks is None: prev_stencils_bmasks = [DEFAULT_STENCILS, DEFAULT_STENCILS]
        if self.pos_strength[player_index, pos_index] == UNKNOWN:
            # If this position was not checked before..

            # Check all available stencils.
            strength, stencils_bmasks = self.status(player_index, pos_index, prev_stencils_bmasks = prev_stencils_bmasks)
            
            if strength != UNKNOWN:
                # If value is not UNKNOWN just give it.
                self.pos_strength[player_index, pos_index] = strength
                return strength
            else:
                # Otherwise we must to check all available moves.
                moves = self.available_moves(player_index, pos_index, stencils_bmasks = stencils_bmasks)
                if UNKNOWN in moves:
                    die('Something strange happened : UNKNOWN returns')
                
                def count_of(strength_value):
                    if strength_value in moves:
                        return len(moves[strength_value])
                    else:
                        return 0

                if count_of(LOSING) > 0 or count_of(LOSING_FINAL) > 0:
                    # If there are some moves to the enemy losing, this position is winning.
                    self.pos_strength[player_index, pos_index] = WINNING
                elif count_of(WINNING) > 0 or count_of(WINNING_FINAL) > 0:
                    # Otherwise the enemy can winning if there is no moves to dead hit.
                    if count_of(DEAD_HIT) == 0:
                        self.pos_strength[player_index, pos_index] = LOSING
                    else:
                        self.pos_strength[player_index, pos_index] = DEAD_HIT
                else:
                    # If there are no moves to winning someone - dead hit
                    self.pos_strength[player_index, pos_index] = DEAD_HIT

                return self.pos_strength[player_index, pos_index]
        else:
            return self.pos_strength[player_index, pos_index]


    def best_way(self, player_index, pos_index):
        """
        The best way for the player which moved from the current position.

        Parameters
        ----------
        player_index  (int):   Player index.
        pos_index  (int):      Position index.
        
        Returns
        ----------
        (int) next state for the player or -1 if there is no moves from the current position.
        """


        stencils_bmasks = [DEFAULT_STENCILS, DEFAULT_STENCILS]
       
        player_label = 'X' if player_index == X_PLAYER else 'O'
        tttoe_mask = tttoe_representation(decimal_to_mask(pos_index))
        enemy_index = (player_index + 1) % 2

        strength = self.calc_position_strength(player_index, pos_index, stencils_bmasks)
        moves = self.available_moves(player_index, pos_index, stencils_bmasks = stencils_bmasks)

        def random_mask(strength):
            moves_count = len(moves[strength]) if strength in moves else 0
            if moves_count > 0: 
                random_index = randint(0, moves_count - 1)
                return moves[strength][random_index]

        ret = -1
        if strength == DEAD_HIT:
            ret = random_mask(DEAD_HIT)
        elif strength == WINNING or strength == WINNING_FINAL:
            mask = random_mask(LOSING)
            ret = mask if mask is not None else random_mask(LOSING_FINAL)  
        elif strength == LOSING or strength == LOSING_FINAL:
            mask = random_mask(WINNING)
            ret = mask if mask is not None else random_mask(WINNING_FINAL)
        if isinstance(ret, str):
            ret = mask_to_decimal(ret)
        return ret

    def set_position(self, new_pos):
        """
        Just set new position.
        """
        self.current_pos = new_pos
                

    def show(self):
        """
        The text output for the current position.
        """
        pos_mask = tttoe_representation(decimal_to_mask(self.current_pos))
        for (start, end) in [(0, 3), (3, 6), (6, 9)]:
            print pos_mask[start:end]
        

def main():
    game = TicTacToe('        ')
    game.show()

    player = X_PLAYER
    while True:
        if player == X_PLAYER:
            print 'Player X.'
        else:
            print 'Player O.'
        if player == X_PLAYER:
            x = input() - 1
            y = input() - 1

            index = x * 3 + y
            current_pos = game.current_pos
            current_mask = tttoe_representation(decimal_to_mask(current_pos))

            if current_mask[index] == ' ':
                next_mask = current_mask[:index] + 'X' + current_mask[index + 1:]
                game.set_position(mask_to_decimal(next_mask))
            else:
                print('Wrong position! There is %s label in %dx%d position now.' % (current_mask[index], x + 1, y + 1))
                continue
        else:
            game.current_pos = game.best_way(player, game.current_pos)

        if game.current_pos == -1:
            print 'Dead hit.'
            break
        else:
            print '_____'
            game.show()
            print '_____'
            player = (player + 1) % 2
            status, _ = game.status(player, game.current_pos)
            if status == LOSING_FINAL:
                if player == O_PLAYER:
                    print 'X player win.'
                else:
                    print 'O player win.'
                break


if __name__=='__main__':
    main()