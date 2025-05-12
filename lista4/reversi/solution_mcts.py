#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Agent do gry w reversi bazujący na MCTS
'''

import sys


class Reversi:
    M = 8
    DIRS = [(0, 1), (1, 0), (-1, 0), (0, -1),
            (1, 1), (-1, -1), (1, -1), (-1, 1)]
    CORNERS = {(0, 0), (0, 7), (7, 0), (7, 7)}

    def __init__(self):
        from mcts_tree import MCTSNode

        self.board = [[None] * self.M for _ in range(self.M)]
        self.board[3][3] = 1
        self.board[4][4] = 1
        self.board[3][4] = 0
        self.board[4][3] = 0
        self.fields = {(x, y) for y in range(self.M) for x in range(self.M)
                       if self.board[y][x] is None}
        self.history = []
        self.move_list = []
        self.mcts_tree = MCTSNode()

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
            if self.board[fy][fx] is not None:
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

    # ------------------------ MCTS ------------------------
    def hash_board(self):
        return tuple(tuple(row) for row in self.board)

    def mcts_iterations(self, my_player, iterations=500, time_limit=1):
        from time import time
        from copy import deepcopy

        start_time = time()

        for _ in range(iterations):
            if time_limit and time() - start_time > time_limit:
                break

            # Kopiujemy stan gry
            game_copy = deepcopy(self)

            # 1. Selekcja - znajdujemy węzeł do rozwinięcia wraz z modyfikowaniem stanu gry
            selected_node, path = self.mcts_tree.select(game_copy)

            # 2. Ekspansja - dodajemy nowy węzeł (jeśli nie jest terminalny)
            if not game_copy.terminal() and game_copy.moves(len(game_copy.move_list) % 2):
                new_node = selected_node.expand(game_copy)
                # 3. Symulacja - przeprowadzamy losową grę
                result = new_node.simulate(game_copy, my_player)
                # 4. Ewaluacja - aktualizujemy statystyki w górę drzewa
                new_node.evaluate(game_copy, result)
            else:
                # Węzeł terminalny - oceniamy bezpośrednio
                result = selected_node.simulate(game_copy, my_player)
                selected_node.evaluate(game_copy, result)

        return self.mcts_tree

    def run_mcts(self, my_player):
        # Uruchamiamy iteracje MCTS
        self.mcts_iterations(my_player)

        # Wybieramy najlepszy ruch
        possible_moves = self.moves(my_player)

        if not possible_moves:
            return None

        best_move = None
        most_visits = -1

        for move in possible_moves:
            if move in self.mcts_tree.children:
                child = self.mcts_tree.children[move]
                if child.games_played > most_visits:
                    most_visits = child.games_played
                    best_move = move

        # Jeśli nie znaleziono żadnego ruchu, wybierz losowy
        if best_move is None and possible_moves:
            from random import choice
            best_move = choice(possible_moves)

        # Wykonaj wybrany ruch
        self.do_move(best_move, my_player)

        # Aktualizuj drzewo MCTS
        if best_move in self.mcts_tree.children:
            self.mcts_tree = self.mcts_tree.children[best_move]
            self.mcts_tree.parent = None
        else:
            from mcts_tree import MCTSNode
            self.mcts_tree = MCTSNode()

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
        return line[0], line[1:]

    def loop(self):
        while True:
            cmd, args = self.hear()
            if cmd == 'HEDID':
                unused_move_timeout, unused_game_timeout = args[:2]
                move = tuple((int(m) for m in args[2:]))
                if move == (-1, -1):
                    move = None
                self.game.do_move(move, 1 - self.my_player)
            elif cmd == 'ONEMORE':
                self.reset()
                continue
            elif cmd == 'BYE':
                break
            else:
                assert cmd == 'UGO'
                assert not self.game.move_list
                self.my_player = 0

            move = self.game.run_mcts(self.my_player)
            # print("solution says: ", move, file=sys.stderr)
            if move is None:
                self.say('IDO -1 -1')
            else:
                self.say('IDO %d %d' % move)


if __name__ == '__main__':
    player = Player()
    player.loop()
