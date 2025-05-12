from typing import override

from my_jungle import Jungle
from copy import copy

"""
W tym zadaniu zaimplementuję alpha-beta search
"""


import random
import sys
from copy import deepcopy

class Jungle4(Jungle):
    DRAW_VALUE = 0.5

    def __init__(self):
        super().__init__()
        pieces_copy = deepcopy(self.pieces)
        self.history = [pieces_copy]

    def _distance(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def _dynamic_depth(self, current_depth, num_moves):
        if num_moves == 1:
            return current_depth + 1
        elif num_moves > 7:
            return current_depth - 2
        elif num_moves < 4:
            return current_depth
        return current_depth - 1

    @override
    def do_move(self, start: (int, int), end: (int, int), player: int):
        super().do_move(start, end, player)
        pieces_copy = deepcopy(self.pieces)
        self.history.append(pieces_copy)

    def undo_move(self):
        assert len(self.history) > 0
        self.history.pop()
        self.pieces = deepcopy(self.history[-1])

    def evaluate(self, player):
        w = self.get_winner()
        if w is not None:
            return 1_000_000 if w == player else -1_000_000

        my_pieces = self.pieces[player]["positions"]
        opp_pieces = self.pieces[1 - player]["positions"]

        my_count = len(my_pieces)
        opp_count = len(opp_pieces)

        my_den = self.DENS[1 - player]
        opp_den = self.DENS[player]

        # Suma odległości do jamy przeciwnika (im mniejsza tym lepiej)
        my_sum_dist = sum(self._distance(pos, my_den) for pos in my_pieces)
        opp_sum_dist = sum(self._distance(pos, opp_den) for pos in opp_pieces)

        # Bliskość do jamy przeciwnika — im bliżej tym lepiej
        my_closest = min((self._distance(pos, my_den) for pos in my_pieces), default=100)
        opp_closest = min((self._distance(pos, opp_den) for pos in opp_pieces), default=100)

        return (
                10 * (my_count - opp_count)
                + 2 * (opp_sum_dist - my_sum_dist)
                + 5 * (opp_closest - my_closest)
        )

    def alpha_beta_helper(self, depth, alpha, beta, current_player, perspective_player, time_limit, time_start):
        if depth <= 0 or self.get_winner() is not None:
            return self.evaluate(perspective_player)

        moves = self.generate_all_moves(current_player)
        depth = self._dynamic_depth(depth, len(moves))
        if not moves:
            self.do_move((-1, -1), (-1, -1), current_player)
            next_player = 1 - current_player
            score = self.alpha_beta_helper(depth - 1, alpha, beta, next_player, perspective_player, time_limit,
                                           time_start)
            self.undo_move()
            return score


        if current_player == perspective_player:
            value = float('-inf')
            for move in moves:
                self.do_move(move[0], move[1], current_player)
                score = self.alpha_beta_helper(depth - 1, alpha, beta, 1 - current_player, perspective_player,
                                               time_limit, time_start)
                self.undo_move()
                value = max(value, score)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for move in moves:
                self.do_move(move[0], move[1], current_player)
                score = self.alpha_beta_helper(depth - 1, alpha, beta, 1 - current_player, perspective_player,
                                               time_limit, time_start)
                self.undo_move()
                value = min(value, score)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def alpha_beta_search(self, player, max_depth=4, time_limit=0.5, time_start=None):
        best_score = float('-inf')
        best_move = ((-1, -1), (-1, -1))

        for start, end in self.generate_all_moves(player):
            self.do_move(start, end, player)
            score = self.alpha_beta_helper(max_depth - 1, float('-inf'), float('inf'), 1 - player, player, time_limit,
                                           time_start)
            self.undo_move()
            if score > best_score:
                best_score = score
                best_move = (start, end)
        self.do_move(best_move[0], best_move[1], player)
        return best_move


class Player(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.game = Jungle4()
        self.my_player = 1
        self.say('RDY')

    def say(self, what):
        sys.stdout.write(what)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def hear(self):
        line = sys.stdin.readline().split()
        return line[0], line[1:]

    def loop(self):
        while True:
            cmd, args = self.hear()
            if cmd == 'HEDID':
                unused_move_timeout, unused_game_timeout = args[:2]
                move = tuple((int(m) for m in args[2:]))
                xs, ys, xd, yd = move
                self.game.do_move((xs, ys), (xd, yd), 1-self.my_player)
            elif cmd == 'ONEMORE':
                self.reset()
                continue
            elif cmd == 'BYE':
                break
            else:
                assert cmd == 'UGO'
                self.my_player = 0

            start, end = self.game.alpha_beta_search(self.my_player)
            self.say('IDO %d %d %d %d' % (start[0], start[1], end[0], end[1]))


if __name__ == '__main__':
    player = Player()
    player.loop()