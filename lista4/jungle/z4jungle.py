from typing import override

from my_jungle import Jungle
from copy import copy, deepcopy
import random
import sys
from time import time

"""
W tym zadaniu zaimplementuję alpha-beta search
"""



class Jungle4(Jungle):
    DRAW_VALUE = 0.5
    PIECE_VALUES = {
        "e": 8,
        "l": 7,
        "t": 6,
        "j": 4,
        "w": 3,
        "d": 2,
        "c": 1,
        "r": 4,
        "E": 8,
        "L": 7,
        "T": 6,
        "J": 4,
        "W": 3,
        "D": 2,
        "C": 1,
        "R": 4
    }

    def __init__(self):
        super().__init__()
        pieces_copy = deepcopy(self.pieces)
        self.transposition_table = {}
        self.history = [pieces_copy]
        self.start_time = 0
        self.time_limit = 5
        self.best_move = None
        self.search_interrupted = False

    def is_time_up(self):
        return time() - self.start_time > self.time_limit * 0.95

    def _distance(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def _zobrist_hash(self):
        result = 0
        for player in [0, 1]:
            for piece, pos in self.pieces[player]["animals"].items():
                result ^= hash((player, piece, pos))
        return result

    def _dynamic_depth(self, current_depth, num_moves):
        if num_moves == 1:
            return current_depth + 1
        elif num_moves > 25:
            return current_depth - 2
        elif num_moves < 15:
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

        my_value = sum(Jungle4.PIECE_VALUES[p] for p in self.pieces[player]["animals"].keys())
        opp_value = sum(Jungle4.PIECE_VALUES[p] for p in self.pieces[1 - player]["animals"].keys())

        my_den = self.DENS[1 - player]
        opp_den = self.DENS[player]

        # suma odległości do jamy przeciwnika (im mniejsza tym lepiej)
        my_sum_dist = sum(self._distance(pos, my_den) for pos in my_pieces)
        opp_sum_dist = sum(self._distance(pos, opp_den) for pos in opp_pieces)

        # odległość najlepszego pionka do jamy przeciwnika — im bliżej tym lepiej
        my_closest = min((self._distance(pos, my_den) for pos in my_pieces), default=100)
        opp_closest = min((self._distance(pos, opp_den) for pos in opp_pieces), default=100)

        return (
                10 * (my_value - opp_value)
                + 2 * (opp_sum_dist - my_sum_dist)
                + 5 * (opp_closest - my_closest)
        )

    def sorted_moves(self, moves, player, perspective_player, maximizing, depth=None):
        if depth is not None and depth < 4:
            return moves

        evaluated = []
        for move in moves:
            self.do_move(move[0], move[1], player)
            score = self.evaluate(perspective_player)
            self.undo_move()
            evaluated.append((score, move))

        evaluated.sort(reverse=maximizing)
        return [move for score, move in evaluated]

    def alpha_beta_helper(self, depth, alpha, beta, current_player, perspective_player):
        if self.is_time_up():
            self.search_interrupted = True
            return self.evaluate(perspective_player)

        state_hash = self._zobrist_hash()
        if state_hash in self.transposition_table and self.transposition_table[state_hash][0] >= depth:
            return self.transposition_table[state_hash][1]

        if depth <= 0 or self.get_winner() is not None:
            eval_score = self.evaluate(perspective_player)
            self.transposition_table[state_hash] = (depth, eval_score)
            return eval_score

        moves = self.generate_all_moves(current_player)
        depth = self._dynamic_depth(depth, len(moves))
        if not moves:
            self.do_move((-1, -1), (-1, -1), current_player)
            next_player = 1 - current_player
            score = self.alpha_beta_helper(depth - 1, alpha, beta, next_player, perspective_player)
            self.undo_move()
            return score

        moves = self.sorted_moves(moves, current_player, perspective_player, current_player == perspective_player,
                                  depth)
        if current_player == perspective_player:
            value = float('-inf')
            for move in moves:
                if self.is_time_up():
                    self.search_interrupted = True
                    break
                self.do_move(move[0], move[1], current_player)
                score = self.alpha_beta_helper(depth - 1, alpha, beta, 1 - current_player, perspective_player)
                self.undo_move()
                value = max(value, score)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for move in moves:
                if self.is_time_up():
                    self.search_interrupted = True
                    break
                self.do_move(move[0], move[1], current_player)
                score = self.alpha_beta_helper(depth - 1, alpha, beta, 1 - current_player, perspective_player)
                self.undo_move()
                value = min(value, score)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def alpha_beta_search(self, player, max_depth=4, time_limit=3):
        self.start_time = time()
        self.time_limit = time_limit
        self.search_interrupted = False

        moves = self.generate_all_moves(player)
        if not moves:
            return ((-1, -1), (-1, -1))

        best_score = float('-inf')
        best_move = moves[0]

        for start, end in moves:
            if self.is_time_up():
                break
            self.do_move(start, end, player)
            score = self.alpha_beta_helper(max_depth - 1, float('-inf'), float('inf'), 1 - player, player)
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
        move_timeout = 5
        while True:
            cmd, args = self.hear()
            if cmd == 'HEDID':
                unused_move_timeout, unused_game_timeout = args[:2]
                move_timeout = float(unused_move_timeout)
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

            start, end = self.game.alpha_beta_search(self.my_player, time_limit=move_timeout)
            self.say('IDO %d %d %d %d' % (start[0], start[1], end[0], end[1]))


if __name__ == '__main__':
    player = Player()
    player.loop()