#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 0 - lowercase player
# 1 - uppercase player
# !/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Losowy agent do Dżungli
'''

import random
import sys
from copy import deepcopy

from my_jungle import Jungle


class Jungle3(Jungle):
    DRAW_VALUE = 0.5

    # zwracam depth bo może później będę chciała uzależniać od głębokości jeszcze
    def simulate_random(self, active_player, max_depth=50):
        depth = 0
        player = active_player
        while True:
            w = self.get_winner()
            if w is not None:
                return w, depth
            moves = self.generate_all_moves(player)
            if not moves or depth >= max_depth:
                return None, depth
            mv = random.choice(moves)
            self.do_move(mv[0], mv[1], player)
            player = 1 - player
            depth += 1

    def choose_mc_move(self, player, sims_budget=50):
        moves = self.generate_all_moves(player)
        if not moves:
            return None

        sims_per_move = max(1, sims_budget // len(moves))
        best = None
        best_score = -1.0

        for mv in moves:
            total = 0.0
            for _ in range(sims_per_move):
                g_copy = deepcopy(self)
                g_copy.do_move(mv[0], mv[1], player)
                winner, _ = g_copy.simulate_random(1 - player)
                if winner == player:
                    total += 1.0
                elif winner is None:
                    total += Jungle3.DRAW_VALUE
            avg = total / sims_per_move
            if avg > best_score:
                best_score = avg
                best = mv

        return best




class Player(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.game = Jungle3()
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
                # assert not self.game.move_list
                self.my_player = 0

            mv = self.game.choose_mc_move(self.my_player)
            if mv is None:
                # brak ruchów
                self.say('IDO -1 -1 -1 -1')
            else:
                (xs, ys), (xd, yd) = mv
                self.game.do_move((xs, ys), (xd, yd), self.my_player)
                self.say(f'IDO {xs} {ys} {xd} {yd}')


if __name__ == '__main__':
    player = Player()
    player.loop()