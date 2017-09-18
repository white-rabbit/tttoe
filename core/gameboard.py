from os.path import abspath, dirname, exists, join

from bifilter import BinaryFilter
from utils import enum, memoized_by_uid

import pickle

BASE = 3
LABELS = " XO"
E_LABEL, X_LABEL, O_LABEL = LABELS

STATUS = enum('DRAW', 'WINNING', 'LOSING', 'WINNING_FINAL', 'LOSING_FINAL', 'IMPOSSIBLE', 'UNKNOWN')


class GameBoardException(Exception):
    def __init__(self, message):
        super(GameBoardException, self).__init__(message)


class GameBoard(object):
    def __init__(self, height, width):
        """
        Game board.

        Parameters
        ----------
        height  (int):   tic tac toe board height.
        width   (int):   tic tac toe board width.
        """
        self.height = height
        self.width = width
        # width of text mask
        self.tmask_width = height * width
        # maximal count of game board states
        self.pos_count = BASE**self.tmask_width
        # the current position in the text representation
        self.position = ' ' * self.tmask_width
        # stencils for winning position checking
        self.stencils = self.__make_stencils(height, width)
        # Bitmask of allowed stencils, default is 11111..111 - checking of all stencils make sense
        self.default_stencils_filter = BinaryFilter(len(self.stencils))
        # equivalent game board transformations by using permutations
        self.eq_permutations = self.__equivalent_permutations()
        # parametrized memoization or dumped strategy
        self.cur_dir = dirname(abspath(__file__))

        dump_path = join(self.cur_dir, join('dump','%d_%d_dump.pkl' % (height, width)))
        memo_dump = dump_path if exists(dump_path) else None
        self.position_strength = self.memoized(self.position_strength, memo_dump = memo_dump)


    def __make_stencils(self, height, width):
        """
        This method makes winning position stencils.

        Parameters
        ----------
        width  (int):   tic tac toe board width.
        
        Returns
        ----------
        (list) list of stencil indicies.
        """
        winning_len = min(height, width)
        delta = max(height, width) - winning_len + 1
        
        indexar = []
        rows = []
        for i in xrange(height):
            indexar.append(range(i * width, (i + 1) * width))
            for shift in xrange(0, width - winning_len + 1):
                rows.append(range(i * width + shift, i * width + winning_len + shift))

        cols = []
        for i in xrange(width):
            for shift in xrange(0, height - winning_len + 1):
                cols.append(map(lambda x : x[i], indexar[shift:shift + winning_len]))


        diags = [[] for _ in xrange(2 * delta)]
        for shift in xrange(delta):
            for i in xrange(winning_len):
                shift_i, shift_j = (shift, 0) if height > winning_len else (0, shift)
                diags[shift * 2].append(indexar[i + shift_i][i + shift_j])
                diags[shift * 2 + 1].append(indexar[height - shift_i - i - 1][i + shift_j])

        return rows + cols + diags

    def __equivalent_permutations(self):
        """
        This method makes permutations of equivalent positions (rotation etc..).
        
        Returns
        ----------
        (list) a list of permutations.
        """
        bh = self.height
        bw = self.width

        permutations = []
        identity = range(self.tmask_width)
        rows = [identity[li * bw: (li + 1) * bw] for li in xrange(bh)]
        #mirrored rows
        mirrored_rows = [r[::-1] for r in rows]

        add = lambda a, b : a + b

        # top-down inversion
        permutations.append(reduce(add, rows[::-1]))

        # left-right inversion
        permutations.append(reduce(add, mirrored_rows))

        # both left-right and top-down inversions
        permutations.append(reduce(add, mirrored_rows[::-1]))

        if bh == bw:
            cols = []
            for i in xrange(bw):
                cols.append(map(lambda x : x[i], rows))
            mirrored_cols = [c[::-1] for c in cols]
            # left rotation
            permutations.append(reduce(add, cols[::-1]))
            # right rotation
            permutations.append(reduce(add, mirrored_cols))

        return permutations
            

    def __status(self, position, stencils_filter = None):
        """
        Obvious information about some position by using stencils.

        Parameters
        ----------
        position  (str):   a position in the text representation.
       
        Returns
        ----------
        (int) strength for current player
        (int) list of two integer values : bitmasks for the first and the second players after checking.
        """
        if stencils_filter is None: stencils_filter = self.default_stencils_filter

        # initial value of position strength for current player
        strength_for_current_player = STATUS.UNKNOWN
        
        # Count of first and second players winning combination.
        # This list is used for IMPOSSIBLE positions detection. 
        wining_count = [0, 0]

        # Current bitmasks are at least like previous bitbasks.
        new_stencils_filter = BinaryFilter(stencils_filter)

        # indicies of labels in LABELS global variable
        E_IND, X_IND, O_IND = LABELS.index(E_LABEL), LABELS.index(X_LABEL), LABELS.index(O_LABEL)
        
        
        # indicies of players
        X_PLAYER, O_PLAYER = 0, 1

        player_label = self.player_label(position)
        player_index = X_PLAYER if player_label == X_LABEL else O_PLAYER

        for i in stencils_filter.indicies():
            stencil = self.stencils[i]
            label_count = [0, 0, 0]
            # The count of every kind labels calculation for the current stencil.
            for index in stencil:
                label_index = LABELS.index(position[index])
                label_count[label_index] += 1

            if label_count[X_IND] != 0 and label_count[O_IND] != 0:
                # 'X' and 'O' labels inside this stencil: 
                # this stencil is not need anymore.
                new_stencils_filter.drop_index(i)                      
            elif label_count[X_IND] != 0 and label_count[E_IND] == 0:
                # if count of an empty labels is zero - X player win.
                wining_count[X_PLAYER] += 1
            elif label_count[O_IND] != 0 and label_count[E_IND] == 0:
                # Similarly.
                wining_count[O_PLAYER] += 1

        total_winings = sum(wining_count)
        if total_winings == 0:
            if new_stencils_filter.empty():
                strength_for_current_player = STATUS.DRAW
            else:
                strength_for_current_player = STATUS.UNKNOWN
        elif total_winings > 0:
            if wining_count[player_index] == total_winings:
                strength_for_current_player = STATUS.IMPOSSIBLE
            else:
                strength_for_current_player = STATUS.LOSING_FINAL
        else:
            strength_for_current_player = STATUS.IMPOSSIBLE

        if strength_for_current_player == STATUS.IMPOSSIBLE:
            message = 'Something strange happened : STATUS.IMPOSSIBLE returned in method GameBoard.__status.'
            raise GameBoardException(message)

        return strength_for_current_player, new_stencils_filter

    def player_label(self, position):
        """
        This method determines the label of the current player by position.

        Parameters
        ----------
        position  (str):   a position in the text representation

        Returns
        ----------
        (str) X or O label for the next moving player in the position
        """
        count_X = position.count(X_LABEL)
        count_O = position.count(O_LABEL)
        if count_X == count_O:
            return 'X'
        elif count_O + 1 == count_X:
            return 'O'
        else:
            raise GameBoardException('Position is not possible. X label count = %d and O label count = %d.' % (count_X, count_O))

    def label(self, I, J):
        i, j = I - 1, J - 1
        if 0 <= i < self.height and 0 <= j < self.width:
            index = i * self.width + j
            return self.position[index]
        else:
            message = ''
            if not (1 <= I <= self.height):
                m_mask = 'Wrong position indicies: the first index %d must be in range [1, %d]\n'
                message += m_mask % (I, self.height)
            if not (1 <= J <= self.width):
                m_mask = 'Wrong position indicies: the second index %d must be in range [1, %d]\n'
                message = m_mask % (J, self.width)

            raise GameBoardException(message)

    def update_position(self, I, J):
        """
        Update position on game board.

        Parameters
        ----------
        I  (int):            the first coordinate (from 1 to height).
        J  (int):            the second coordinate (from 1 to width).
        player_label (str) : the label of the player
        """
        i, j = I - 1, J - 1
        index = i * self.width + j
        if self.label(I, J) == ' ':            
            
            player_label = self.player_label(self.position)
            self.position = self.position[:index] + player_label + self.position[index + 1:]
        else:
            m_mask = "Wrong position indicies: the label %s is already in the position (%d, %d)"
            message = m_mask % (self.position[index], I, J)
            raise GameBoardException(message)
        
        
    def unique_id(self, position):
        """ 
        Returns
        ----------
        (int) unque id for current postion

        """
        ternary = position
        # replacing ' ', 'X', 'O' by '0','1','2' 
        for label in LABELS:
            numeral = str(LABELS.index(label))
            ternary = ternary.replace(label, numeral)

        # list of equivalent positions in ternary notations
        equivalent_positions = [ternary]

        add = lambda a, b : a + b
        get_symbol = lambda i : ternary[i]
        # makes list of equivalent positions by symbols permutation
        for p in self.eq_permutations:
            p_pos = reduce(add, map(get_symbol, p))
            equivalent_positions.append(p_pos)
        # convert numbers in ternary notation (str) to decimal values (int)
        ternary_to_decimal = lambda x : int(x, 3)
        return min(map(ternary_to_decimal, equivalent_positions))

    def available_positions(self, position, stencils_filter = None):
        """
        List of avalable positions for the player which moved from current position.
        Parameters
        ----------
        pos_index  (int):             Position index.
        prev_stencils_bmasks (list):  A list of available stencils bitmasks for the first and the second player.        
        Returns
        ----------
        (dict) available positions - dictionary that collecting lists of masks for strength values. 
        """
        if stencils_filter is None: stencils_filter = self.default_stencils_filter
        # Internal representation of current position.
        player_label = self.player_label(position)

        # Total count of positions
        positions = dict()

        for i, label in enumerate(position):
            if label == ' ':
                # A mask for the next move.
                next_position = position[:i] + player_label + position[i + 1:]
                # Recursion call for the next move.
                this_move_enemy_strength = self.position_strength(next_position, stencils_filter = stencils_filter)
                if this_move_enemy_strength in positions:
                    positions[this_move_enemy_strength].append(next_position)
                else:
                    positions[this_move_enemy_strength] = [next_position]

        if STATUS.UNKNOWN in positions:
            message = 'Something strange happened : STATUS.UNKNOWN returned in method GameBoard.position_strength.'
            raise GameBoard(message)
        return positions



    def position_strength(self, position, stencils_filter = None):
        """
        Position strength for the player which moved from current position.

        Parameters
        ----------
        pos_index  (int):                Position index.
        stencils_filter (BinaryFilter):  A list of available stencils bitmasks for the first and the second player.        

        Returns
        ----------
        (int) position strength for current player.
        """
        # setting default value for both stencils

        if stencils_filter is None: stencils_filter = self.default_stencils_filter
        strength, actual_filter = self.__status(position, stencils_filter = stencils_filter)
        
        if strength != STATUS.UNKNOWN:
            return strength
        else:
            # Otherwise we must to check all available positions.
            available_positions = self.available_positions(position, stencils_filter = stencils_filter)

            def count_of(strength_value):
                if strength_value in available_positions:
                    return len(available_positions[strength_value])
                else:
                    return 0

            strength = STATUS.UNKNOWN
            if count_of(STATUS.LOSING) > 0 or count_of(STATUS.LOSING_FINAL) > 0:
                # If there are some moves to the enemy losing, this position is winning.
                strength = STATUS.WINNING
            elif count_of(STATUS.WINNING) > 0 or count_of(STATUS.WINNING_FINAL) > 0:
                # Otherwise the enemy can winning if there is no moves to draw.
                if count_of(STATUS.DRAW) == 0:
                    strength = STATUS.LOSING
                else:
                    strength = STATUS.DRAW
            else:
                # If there are no moves to winning someone - draw
                strength = STATUS.DRAW

            return strength

    def memoized(self, func, memo_dump=None):
        """
        Memoization of some class method.
        Parameters
        ----------
        func  (callable): class method.
        memo_dump (str) : path to memory dump (dictionary in .pkl file format) or None.

        Returns
        ----------
        wrapped function 'func' 
        """        
        self.memory = {} if memo_dump is None else self.load_memory_dump(memo_dump)
        def wrapped(*args, **kwargs):
            uid = self.unique_id(args[0])
            if uid in self.memory:
                return self.memory[uid]
            else:
                value = func(*args, **kwargs)
                self.memory[uid] = value
                return value

        return wrapped

    def save_memory_dump(self, fname):
        """
        Save dictionary to .pkl file.
        
        Parameters
        ----------
        fname (str) path to output file.
        """
        with open(fname, 'wb') as f:
            pickle.dump(self.memory, f, pickle.HIGHEST_PROTOCOL)

    def load_memory_dump(self, fname):
        """
        Load dictionary from .pkl file.
        
        Parameters
        ----------
        fname (str) path to input file.
        """
        with open(fname, 'rb') as f:
            return pickle.load(f)

    def winning_indicies(self):
        # indicies of labels in LABELS global variable
        E_IND, X_IND, O_IND = LABELS.index(E_LABEL), LABELS.index(X_LABEL), LABELS.index(O_LABEL)
        position = self.position
        winning_stencils = []
        for stencil in self.stencils:        
            label_count = [0, 0, 0]
            # The count of every kind labels calculation for the current stencil.
            for index in stencil:
                label_index = LABELS.index(position[index])
                label_count[label_index] += 1

            if label_count[X_IND] != 0 and label_count[O_IND] != 0:
                # 'X' and 'O' labels inside this stencil
                pass
            elif label_count[X_IND] != 0 and label_count[E_IND] == 0:
                # if count of an empty labels is zero - X player win.
                winning_stencils.append(stencil)
            elif label_count[O_IND] != 0 and label_count[E_IND] == 0:
                # Similarly.
                winning_stencils.append(stencil)

        winning_indicies = []
        coordinates_2d = [(i + 1, j +1) for i in xrange(self.height) for j in xrange(self.width)]
        
        for ws in winning_stencils:
            winning_indicies.append(map(lambda x : coordinates_2d[x], ws))

        return winning_indicies

    def status(self):
        """
        The status of the current game board position.self
        Returns
        -----------
        (str) text description of current position
        """
        status = self.__status(self.position)
        player_label = self.player_label(self.position)
        enemy_label = 'X' if player_label == 'O' else 'O'

        if status[0] == STATUS.LOSING_FINAL:
            return enemy_label + ' player win'
        elif status[0] == STATUS.WINNING_FINAL:
            return player_label + ' player win'
        elif status[0] == STATUS.DRAW:
            return 'DRAW'
        else:
            return 'GAME'

    def game_over(self):
        if self.position.count(' ') == 0:
            return True
        else:
            status = self.__status(self.position)
            return status[0] in [STATUS.LOSING_FINAL, STATUS.WINNING_FINAL]

def main():
    for w, h in [(3,3), (3, 4), (4, 3)]:
        gb = GameBoard(h, w)
        print 'Game tree calculation for board size', h, w
        print 'It may takes a several minutes... Please wait.'
	
        from time import time
        t = time()
        gb.position_strength(gb.position)
        time() - t
        path_to_dump = join(gb.cur_dir, 'dump')
        if not exists(path_to_dump):
            from os import mkdir
            mkdir(path_to_dump)
        print 'dump to %s' % path_to_dump
        gb.save_memory_dump(join(path_to_dump, '%d_%d_dump.pkl' % (gb.height, gb.width)))
 
if __name__=='__main__':
    main()
