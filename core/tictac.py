# The tic-tac-toe game base class.

# external imports:
import numpy
from copy import deepcopy

# internal imports:
from utils import *

from ternary import POS_COUNT, E_IND, X_IND, O_IND
from ternary import decimal_to_mask, mask_to_decimal, canonical_representation, tttoe_representation
from bitop import bit_up, bit_down, is_up


# pos strengths
UNKNOWN = -1
DEAD_HIT = 0
WINNING = 1
LOSING = 2
WINNING_FINAL = 3
LOSING_FINAL = 4
IMPOSSIBLE = 5

# STENCILS
STENCILS  = [[0,1,2], [3,4,5], [6, 7, 8]] # 0) !!!|...|... 1) ...|!!!|... 2) ...|...|!!!
STENCILS += [[0,3,6], [1,4,7], [2, 5, 8]] # 3) !..|!..|!.. 4) .!.|.!.|.!. 5) ..!|..!|..!
STENCILS += [[0,4,8], [2,4,6]]            # 6) !..|!..|!.. 7) .!.|.!.|.!.
DEFAULT_STENCILS = 2**len(STENCILS) - 1

# Players
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
        self.pos_strength = numpy.zeros((2, POS_COUNT), numpy.int16) - 1

        
    
    def obvious_info(self, player_index, pos_index, prev_stencils_bmask):
        """
        Obvious information about some position by using stencils.

        Parameters
        ----------
        player_index  (int):   Player index.
        pos_index  (int):   Position index.
        stencil_bmask (int):   Bitmask of available stencils.
        
        Returns

        ----------

        """
        pos_mask = canonical_representation(decimal_to_mask(pos_index))

        position_strength_for_player = UNKNOWN
        wining_count = [0, 0]

        stencils_bmask = deepcopy(prev_stencils_bmask)
        common_bmask = stencils_bmask[0] | stencils_bmask[1]

        for i, stencil in enumerate(STENCILS):
            if is_up(common_bmask, i):

                label_count = [0,0,0]
                # the every kind labels count calculation for the current stencil
                for index in stencil:
                    label_count[int(pos_mask[index])] += 1
                if label_count[X_IND] != 0 and label_count[O_IND] != 0:
                    stencils_bmask[X_PLAYER] = bit_down(stencils_bmask[X_PLAYER], i)
                    stencils_bmask[O_PLAYER] = bit_down(stencils_bmask[O_PLAYER], i)                        
                elif label_count[X_IND] != 0:
                    stencils_bmask[O_PLAYER] = bit_down(stencils_bmask[O_PLAYER], i)
                    if label_count[E_IND] == 0: wining_count[X_PLAYER] += 1
                elif label_count[O_IND] != 0:
                    stencils_bmask[X_PLAYER] = bit_down(stencils_bmask[X_PLAYER], i)
                    if label_count[E_IND] == 0: wining_count[O_PLAYER] += 1

        strength_for_current_player = UNKNOWN

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


    def calc_position_strength(self, player_index, pos_index, prev_stencils_bmask):
        if self.pos_strength[player_index, pos_index] == UNKNOWN:
            strength, stencils_bmask = self.obvious_info(player_index, pos_index, prev_stencils_bmask)
            if strength != UNKNOWN:
                self.pos_strength[player_index, pos_index] = strength
                return strength
            else:
                tttoe_mask = tttoe_representation(decimal_to_mask(pos_index))
                player_label = 'X' if player_index == X_PLAYER else 'O'

                enemy_index = (player_index + 1) % 2
                
                ways_count = 0
                ways_strengths_count = [0 for _ in xrange(IMPOSSIBLE + 1)]

                for i in xrange(9):
                    if tttoe_mask[i] == ' ':
                        ways_count += 1

                        tttoe_mask_next = tttoe_mask[:i] + player_label + tttoe_mask[i + 1:]
                        this_way_enemy_strength = self.calc_position_strength(enemy_index, mask_to_decimal(tttoe_mask_next), stencils_bmask)

                        if this_way_enemy_strength == UNKNOWN or this_way_enemy_strength is None:
                            die('Something strange happened : UNKNOWN returns')
                        else:
                            ways_strengths_count[this_way_enemy_strength] += 1

                if ways_strengths_count[LOSING] > 0 or ways_strengths_count[LOSING_FINAL] > 0:
                    self.pos_strength[player_index, pos_index] = WINNING
                elif ways_strengths_count[WINNING] > 0 or ways_strengths_count[WINNING_FINAL] > 0:
                    if ways_strengths_count[DEAD_HIT] == 0:
                        self.pos_strength[player_index, pos_index] = LOSING
                    else:
                        self.pos_strength[player_index, pos_index] = DEAD_HIT
                else:
                    self.pos_strength[player_index, pos_index] = DEAD_HIT

                return self.pos_strength[player_index, pos_index]
        else:
            return self.pos_strength[player_index, pos_index]


    def best_way(self, player_index, pos_index):
        player_label = 'X' if player_index == X_PLAYER else 'O'
        tttoe_mask = tttoe_representation(decimal_to_mask(pos_index))
        enemy_index = (player_index + 1) % 2

        stencils_bmask = [DEFAULT_STENCILS, DEFAULT_STENCILS]
        strength = self.calc_position_strength(player_index, pos_index, stencils_bmask)


        count_of_ways = 0
        for i in xrange(9):
            if tttoe_mask[i] == ' ':
                count_of_ways += 1
                tttoe_mask_next = tttoe_mask[:i] + player_label + tttoe_mask[i + 1:]
                tttoe_next_index = mask_to_decimal(tttoe_mask_next)
                this_way_enemy_strength = self.calc_position_strength(enemy_index, tttoe_next_index, stencils_bmask)

                if strength == DEAD_HIT:
                    if this_way_enemy_strength == DEAD_HIT:
                        return tttoe_next_index

                if strength == WINNING or strength == WINNING_FINAL:
                    if this_way_enemy_strength == LOSING or this_way_enemy_strength == LOSING_FINAL:
                        return tttoe_next_index
                    
                if strength == LOSING or strength == LOSING_FINAL:
                    return tttoe_next_index

        if count_of_ways == 0:
            die('DEAD HIT')

    def set_position(self, new_pos):
        self.current_pos = new_pos
                

    def show(self):
        pos_mask = tttoe_representation(decimal_to_mask(self.current_pos))
        for (start, end) in [(0, 3), (3, 6), (6, 9)]:
            print pos_mask[start:end]
        

def main():
    game = TicTacToe('        ')
    game.show()

    player = X_PLAYER
    while True:
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
            game.current_pos = game.best_way(player, game.current_pos)
        print '_____'
        game.show()
        print '_____'
        player = (player + 1) % 2

        status, _ = game.obvious_info(player, game.current_pos, [DEFAULT_STENCILS, DEFAULT_STENCILS])

        if status == LOSING_FINAL:
            if player == O_PLAYER:
                print 'X player win.'
            else:
                print 'O player win.'
            break

        
    print 'this'

if __name__=='__main__':
    main()