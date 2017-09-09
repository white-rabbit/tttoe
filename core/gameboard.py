from bifilter import BinaryFilter
from utils import enum, memoized_by_uid

BASE = 3
LABELS = " XO"
E_LABEL, X_LABEL, O_LABEL = LABELS

STATUS = enum('DRAW', 'WINNING', 'LOSING', 'WINNING_FINAL', 'LOSING_FINAL', 'IMPOSSIBLE', 'UNKNOWN')


class GameBoardException(Exception):
    def __init__(self, message):
        super(GameBoardException, self).__init__(message)


class GameBoard(object):
    def __init__(self, board_height, board_width):
        """
        Game board.

        Parameters
        ----------
        board_width  (int):   tic tac toe board width.
        """
        self.board_height = board_height
        self.board_width = board_width
        # width of text mask
        self.tmask_width = board_height * board_width
        # maximal count of game board states
        self.pos_count = BASE**self.tmask_width
        # the current position in the text representation
        self.position = ' ' * self.tmask_width
        # stencils for winning position checking
        self.stencils = self.__make_stencils(board_height, board_width)
        # Bitmask of allowed stencils, default is 11111..111 - checking of all stencils make sense
        self.default_stencils_filter = BinaryFilter(len(self.stencils))

    def __make_stencils(self, board_height, board_width):
        """
        This method makes winning position stencils.

        Parameters
        ----------
        board_width  (int):   tic tac toe board width.
        
        Returns
        ----------
        (list) list of stencil indicies.
        """
        winning_len = min(board_height, board_width)
        delta = max(board_height, board_width) - winning_len + 1
        
        indexar = []
        rows = []
        for i in xrange(board_height):
            indexar.append(range(i * board_width, (i + 1) * board_width))
            for shift in xrange(0, board_width - winning_len + 1):
                rows.append(range(i * board_width + shift, i * board_width + winning_len + shift))

        cols = []
        for i in xrange(board_width):
            for shift in xrange(0, board_height - winning_len + 1):
                cols.append(map(lambda x : x[i], indexar[shift:shift + winning_len]))


        diags = [[] for _ in xrange(2 * delta)]
        for shift in xrange(delta):
            for i in xrange(winning_len):
                shift_i, shift_j = (shift, 0) if board_height > winning_len else (0, shift)
                diags[shift * 2].append(indexar[i + shift_i][i + shift_j])
                diags[shift * 2 + 1].append(indexar[board_height - shift_i - i - 1][i + shift_j])

        return rows + cols + diags

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
            print position
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

    def inside_board(self, i, j):
        return 0 <= i < self.board_height and 0 <= j < self.board_width

    def index_position(self, i, j):
        return i * self.board_width + j

    def empty_position(self, i, j):
        return self.position[self.index_position(i, j)] == ' '

    def update_position(self, I, J):
        """
        Update position on game board.

        Parameters
        ----------
        i  (int):            the first coordinate.
        j  (int):            the second coordinate.
        player_label (str) : the label of player
        """
        i, j = I - 1, J - 1
        if self.inside_board(i, j):
            index = self.index_position(i, j)
            player_label = self.player_label(self.position)
            if self.position[index] == ' ':
                self.position = self.position[:index] + player_label + self.position[index + 1:]
            else:
                m_mask = "Wrong position indicies: the label %s is already in the position (%d, %d)"
                message = m_mask % (self.position[index], I, J)
                raise GameBoardException(message)
        else:
            message = ''
            if not (1 <= I <= self.board_height):
                m_mask = 'Wrong position indicies: the first index %d must be in range [1, %d]\n'
                message += m_mask % (I, self.board_height)
            if not (1 <= J <= self.board_width):
                m_mask = 'Wrong position indicies: the second index %d must be in range [1, %d]\n'
                message = m_mask % (J, self.board_width)

            raise GameBoardException(message)

    
        
    def unique_id(self, position):
        """ 
        Returns
        ----------
        (int) unque id for current postion

        """
        ternary = position
        for label in LABELS:
            numeral = str(LABELS.index(label))
            ternary = ternary.replace(label, numeral)
        return int(ternary, 3)

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

    @memoized_by_uid
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
                # Otherwise the enemy can winning if there is no moves to dead hit.
                if count_of(STATUS.DRAW) == 0:
                    strength = STATUS.LOSING
                else:
                    strength = STATUS.DRAW
            else:
                # If there are no moves to winning someone - dead hit
                strength = STATUS.DRAW

            return strength

    def status(self):
        status = self.__status(self.position)
        player_label = self.player_label(self.position)
        enemy_label = 'X' if player_label == 'O' else 'O'

        if status[0] == STATUS.LOSING_FINAL:
            print enemy_label, 'Player win'
        elif status[0] == STATUS.WINNING_FINAL:
            print player_label, 'Player win'
        elif status[0] == STATUS.DRAW:
            print 'DRAW'
        else:
            print 'GAME'
    def game_over(self):
        if self.position.count(' ') == 0:
            return True
        else:
            status = self.__status(self.position)
            return status[0] in [STATUS.LOSING_FINAL, STATUS.WINNING_FINAL]

def main():
    gb = GameBoard(3, 3)
    
if __name__=='__main__':
    main()