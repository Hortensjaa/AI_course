#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Mój agent używający alfa - beta searchu
Oparty strukturą na losowym, podanym na dysku.

Zasady ewaluacji:
- pola na planszy są punktowane wg tablicy wartości
    (rogi są najwięcej warte, a pola obok rogów ryzykowne; dokładne wartości znalazłam gdzieś w internecie)

Optymalizacje:
- sortowanie ruchów na "najwyższych" piętrach
- cachowanie rozważonych stanów
- dynamiczne wyliczanie głębokości w zależności od ilości rozgałęzień na danym piętrze
'''


import sys
from time import time


class Reversi:
    M = 8
    DIRS = [(0, 1), (1, 0), (-1, 0), (0, -1),
            (1, 1), (-1, -1), (1, -1), (-1, 1)]
    CORNERS = {(0, 0), (0, 7), (7, 0), (7, 7)}

    def __init__(self):
        self.board = [[None] * self.M for _ in range(self.M)]
        self.board[3][3] = 1
        self.board[4][4] = 1
        self.board[3][4] = 0
        self.board[4][3] = 0
        self.fields = {(x, y) for y in range(self.M) for x in range(self.M)
                       if self.board[y][x] is None}
        self.history = []
        self.move_list = []
        self.transposition_table = {}

    def get(self, x, y):
        if 0 <= x < self.M and 0 <= y < self.M:
            return self.board[y][x]
        return None

    def can_beat(self, x, y, d, player):
        dx, dy = d
        x += dx
        y += dy
        cnt = 0
        while self.get(x, y) == 1 - player:
            x += dx
            y += dy
            cnt += 1
        return cnt > 0 and self.get(x, y) == player

    def moves(self, player):
        return [(x, y) for (x, y) in self.fields
                if any(self.can_beat(x, y, d, player) for d in self.DIRS)]

    def do_move(self, move, player):
        flips = []
        removed_field = None

        if move is None:
            self.history.append((None, flips, removed_field))
            self.move_list.append(None)
            return

        x0, y0 = move
        self.board[y0][x0] = player
        removed_field = move
        self.fields.discard(move)

        for dx, dy in self.DIRS:
            x, y = x0 + dx, y0 + dy
            to_flip = []
            while self.get(x, y) == 1 - player:
                to_flip.append((x, y))
                x += dx
                y += dy
            if self.get(x, y) == player:
                for fx, fy in to_flip:
                    self.board[fy][fx] = player
                flips.extend(to_flip)

        self.history.append((move, flips, removed_field))
        self.move_list.append(move)

    def undo_move(self):
        move, flips, removed_field = self.history.pop()
        self.move_list.pop()

        for fx, fy in flips:
            self.board[fy][fx] = 1 - self.board[fy][fx]

        if move is not None:
            x, y = move
            self.board[y][x] = None
            if removed_field is not None:
                self.fields.add(removed_field)

    def result(self):
        score = 0
        for row in self.board:
            for cell in row:
                if cell == 1:
                    score += 1
                elif cell == 0:
                    score -= 1
        return score

    def terminal(self):
        if not self.fields:
            return True
        if len(self.move_list) < 2:
            return False
        return self.move_list[-1] in [None, (-1, -1)] and self.move_list[-2] in [None, (-1, -1)]

    def hash_board(self):
        return tuple(tuple(row) for row in self.board)

    # ----------------------- EWALUACJA -----------------------

    # pionki na zewnątrz są najbardziej narażone na bicie
    def is_frontier(self, x, y):
        if self.board[y][x] is None:
            return False
        for dx, dy in self.DIRS:
            nx, ny = x + dx, y + dy
            if self.get(nx, ny) is None:
                return True
        return False

    # bonus za stabilność pionków - te, których oponent nie może już przejąć
    # zastosowane uproszczenie - rozważam tylko te na ściankach
    # https://stackoverflow.com/questions/41455456/determining-stable-discs-in-othello
    def is_stable(self, x, y):
        player = self.board[x][y]
        if player == 0:
            return False

        if (x, y) in self.CORNERS:
            return True

        if y == 0 or y == self.M - 1:
            for i in range(x - 1, -1, -1):
                if self.board[i][y] != player:
                    break
                if (i, y) in self.CORNERS:
                    return True
            for i in range(x + 1, self.M):
                if self.board[i][y] != player:
                    break
                if (i, y) in self.CORNERS:
                    return True
            return False

        elif x == 0 or x == self.M - 1:
            for j in range(y - 1, -1, -1):
                if self.board[x][j] != player:
                    break
                if (x, j) in self.CORNERS:
                    return True
            for j in range(y + 1, self.M):
                if self.board[x][j] != player:
                    break
                if (x, j) in self.CORNERS:
                    return True
        return False

    def evaluate(self, player):

        if self.terminal():
            result = self.result()
            if result > 0:
                return 1000000 if player == 1 else -1000000
            elif result < 0:
                return -1000000 if player == 1 else 1000000
            else:
                return 0

        opponent = 1 - player
        score = 0

        weights = [
            [100, -20, 10, 5, 5, 10, -20, 100],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [5, -2, -1, -1, -1, -1, -2, 5],
            [10, -2, -1, -1, -1, -1, -2, 10],
            [-20, -50, -2, -2, -2, -2, -50, -20],
            [100, -20, 10, 5, 5, 10, -20, 100],
        ]

        for y in range(self.M):
            for x in range(self.M):
                piece = self.board[y][x]
                if piece is None:
                    continue

                val = weights[y][x]

                # if self.is_stable(x, y):
                #     val += 5
                # elif self.is_frontier(x, y):
                #     val -= 5

                if piece == player:
                    score += val
                else:
                    score -= val

        return score

    def sorted_moves(self, moves, player, perspective_player, maximizing, depth=None):
        if depth is not None and depth < 4:
            return moves

        evaluated = []
        for move in moves:
            self.do_move(move, player)
            score = self.evaluate(perspective_player)
            self.undo_move()
            evaluated.append((score, move))

        evaluated.sort(reverse=maximizing)
        return [move for score, move in evaluated]

    # ----------------------- ALPHA BETA SEARCH -----------------------
    def dynamic_depth(self, current_depth, num_moves):
        if num_moves == 1:
            return current_depth + 1
        elif num_moves > 7:
            return current_depth - 2
        elif num_moves < 4:
            return current_depth
        return current_depth - 1

    def alpha_beta_helper(self, depth, alpha, beta, current_player, perspective_player, time_limit, time_start):
        if time() - time_start > time_limit - 0.1:
            return self.evaluate(perspective_player)

        key = (self.hash_board(), current_player, depth)

        if key in self.transposition_table:
            return self.transposition_table[key]

        if depth <= 0 or self.terminal():
            return self.evaluate(perspective_player)

        moves = self.moves(current_player)
        depth = self.dynamic_depth(depth, len(moves))
        if not moves:
            self.do_move(None, current_player)
            next_player = 1 - current_player if self.moves(1 - current_player) else current_player
            score = self.alpha_beta_helper(depth - 1, alpha, beta, next_player, perspective_player, time_limit, time_start)
            self.undo_move()
            return score

        sorted_ms = self.sorted_moves(moves, current_player, perspective_player, current_player == perspective_player, depth)
        if current_player == perspective_player:
            value = float('-inf')
            for move in sorted_ms:
                self.do_move(move, current_player)
                score = self.alpha_beta_helper(depth - 1, alpha, beta, 1 - current_player, perspective_player, time_limit, time_start)
                self.undo_move()
                value = max(value, score)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            self.transposition_table[key] = value
            return value
        else:
            value = float('inf')
            for move in sorted_ms:
                self.do_move(move, current_player)
                score = self.alpha_beta_helper(depth - 1, alpha, beta, 1 - current_player, perspective_player, time_limit, time_start)
                self.undo_move()
                value = min(value, score)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            self.transposition_table[key] = value
            return value

    def alpha_beta_search(self, player, max_depth=9, time_limit=0.5, time_start=None):
        best_score = float('-inf')
        best_move = (-1, -1)

        for move in self.moves(player):
            if time() - time_start > time_limit - 0.1:
                break
            self.do_move(move, player)
            score = self.alpha_beta_helper(max_depth - 1, float('-inf'), float('inf'), 1 - player, player, time_limit, time_start)
            self.undo_move()
            if score > best_score:
                best_score = score
                best_move = move

        return best_move


class Player(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.game = Reversi()
        self.my_player = 1
        self.say('RDY')

    def say(self, what):
        sys.stdout.write(what)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def hear(self):
        line = sys.stdin.readline().split()
        # print("solution heard: ", line, file=sys.stderr)
        return line[0], line[1:]

    def loop(self):
        game_time_start = time()
        experiment_time_start = time()
        while True:
            cmd, args = self.hear()
            if cmd == 'HEDID':
                move_timeout, unused_game_timeout = args[:2]
                move_timeout = float(move_timeout)
                move = tuple(int(m) for m in args[2:])
                if move == (-1, -1):
                    move = None
                self.game.do_move(move, 1 - self.my_player)
            elif cmd == 'ONEMORE':
                print("game time: ", time() - game_time_start, file=sys.stderr)
                game_time_start = time()
                self.reset()
                continue
            elif cmd == 'BYE':
                print("Experiment time: ", time() - experiment_time_start, file=sys.stderr)
                break
            else:
                assert cmd == 'UGO'
                game_time_start = time()
                move_timeout = float(args[0])
                assert not self.game.move_list
                self.my_player = 0

            time_start = time()
            move = self.game.alpha_beta_search(
                self.my_player,
                time_limit=move_timeout,
                time_start=time_start
            )
            # print("solution move: ", move, file=sys.stderr)
            self.game.do_move(move, self.my_player)
            self.say('IDO %d %d' % move)


if __name__ == '__main__':
    player = Player()
    player.loop()
