# The tic-tac-toe game base class.

# external imports:
import numpy
from copy import deepcopy

# internal imports:
from utils import die, enum
import stencil
import ternary

from bitop import bit_up, bit_down, is_up
from random import randint


PLAYER_TYPE = enum('ALIVE', 'AI')

class Player(object):
    def __init__(self, player_type=PLAYER_TYPE.ALIVE):
        self.player_type = player_type

    def move(self, position):
        if player_type == PLAYER_TYPE.ALIVE:
            pass
        elif player_type == PLAYER_TYPE.AI:
            next_position = self.AI_next_position(position)
            return move_to(poistion, next_position)

    def move_to(self, position_1, position_2):
        index = -1
        for i in xrange(len(position_1)):
            if position_1[i] != position_2[i]:
                if index == -1:
                    index = i
                else:
                    raise PlayerException('It is not possible to move from %s to %s.' % (position_1, position_2))
        if index != -1:
            return index / position.board_width, index % position.board_width


    def AI_next_position(self, position):
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


        stencils_bmasks = [self.default_stencil, self.default_stencil]
       
        player_label = 'X' if player_index == X_PLAYER else 'O'
        tttoe_mask = tttoe_representation(decimal_to_mask(pos_index))
        enemy_index = (player_index + 1) % 2

        # first four position will filled randomly
        # it can lead to bad moves for AI (used for keeping speed)
        # TODO: something better need :(
        if self.field_width == 4:
            empty = []
            for i, c in enumerate(tttoe_mask):
                if c == ' ': empty.append(i)
            if len(empty) > 12:
                i = empty[randint(0, len(empty) - 1)]
                tttoe_mask_next = tttoe_mask[:i] + player_label + tttoe_mask[i + 1:]
                return mask_to_decimal(tttoe_mask_next)


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

class TicTacToeException(Exception):
    def __init__(self, message):
        super(TicTacToeException, self).__init__(message)


class TicTacToe(object):
    def __init__(self, player1, player2, board):
        self.players = [player1, player2]
        self.game_board = board

    def text_play(self):
        player_index = 0

        while not self.game_board.game_over():
            self.players[current_player].move(self.game_board)
            player_index = (player_index + 1) % 2

        self.game_board.status()




class TicTacToe(object):
    def __init__(self, field_width):
        self.field_width = field_width
        self.current_pos = 0
        # strength of all available positions
        self.pos_strength = [dict(), dict()]
        self.stencils = stencil.generate(field_width)
        self.default_stencil = 2**len(self.stencils) - 1



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


        stencils_bmasks = [self.default_stencil, self.default_stencil]
       
        player_label = 'X' if player_index == X_PLAYER else 'O'
        tttoe_mask = tttoe_representation(decimal_to_mask(pos_index))
        enemy_index = (player_index + 1) % 2

        # first four position will filled randomly
        # it can lead to bad moves for AI (used for keeping speed)
        # TODO: something better need :(
        if self.field_width == 4:
            empty = []
            for i, c in enumerate(tttoe_mask):
                if c == ' ': empty.append(i)
            if len(empty) > 12:
                i = empty[randint(0, len(empty) - 1)]
                tttoe_mask_next = tttoe_mask[:i] + player_label + tttoe_mask[i + 1:]
                return mask_to_decimal(tttoe_mask_next)


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
        for line_index in xrange(self.field_width):
            print pos_mask[line_index * self.field_width: (line_index + 1) * self.field_width]
    
    def end(self):
        tttoe_mask = tttoe_representation(decimal_to_mask(self.current_pos))
        return tttoe_mask.count(' ') == 0


def main():
    FW = -1
    while FW != 3 and FW != 4:
        FW = input('Enter the width of the field. Only values 3 and 4 allowed in the current version.\n')

    ternary.set_field_width(FW)    
    game = TicTacToe(FW)

    game.show()
    player = X_PLAYER
    while True:
        if player == X_PLAYER:
            print 'Player X.'
        else:
            print 'Player O.'
        if player == X_PLAYER:
            x = input('Type x (from 1 to %d) and press Enter\n' % game.field_width) - 1
            y = input('Type y (from 1 to %d) and press Enter\n' % game.field_width) - 1

            index = x * game.field_width + y
            if index < 0 or index > game.field_width ** 2 - 1:
                continue
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


        if not game.current_pos == -1:
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
        elif game.end():
            print 'Dead hit!'
            break
        else:
            continue


if __name__=='__main__':
    main()