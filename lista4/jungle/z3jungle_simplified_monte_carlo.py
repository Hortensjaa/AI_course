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

    def choose_mc_move(self, player, sims_budget=20_000):
        moves = self.generate_all_moves(player)
        if not moves:
            return None, 0

        # na początku (gdy budżet jest duży) oszczędzam ruchy, bo początek gry "nie jest aż taki ważny"
        # w miarę upływu czasu budżet się zmniejsza i ruchy są coraz bardziej istotne
        sims_per_move = min(max(5, 30 - int(0.001 * sims_budget)), 25)
        # print(sims_per_move, file=sys.stderr)
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

        return best, len(moves) * sims_per_move




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
        budget = 20_000
        while True:
            cmd, args = self.hear()
            if cmd == 'HEDID':
                unused_move_timeout, unused_game_timeout = args[:2]
                move = tuple((int(m) for m in args[2:]))
                xs, ys, xd, yd = move
                self.game.do_move((xs, ys), (xd, yd), 1-self.my_player)
            elif cmd == 'ONEMORE':
                print(budget, file=sys.stderr)
                self.reset()
                budget = 20_000
                continue
            elif cmd == 'BYE':
                print(budget, file=sys.stderr)
                break
            else:
                assert cmd == 'UGO'
                budget = 20_000
                self.my_player = 0

            mv, n = self.game.choose_mc_move(self.my_player, budget)
            budget -= n
            # print(n, " - ", budget, file=sys.stderr)
            if mv is None:
                # brak ruchów
                self.say('IDO -1 -1 -1 -1')
            else:
                (xs, ys), (xd, yd) = mv
                self.game.do_move((xs, ys), (xd, yd), self.my_player)
                self.say(f'IDO {xs} {ys} {xd} {yd}')

    # while budget > 0:
    #     for move in moves:
    #         cost = run(move)
    #         budget -= cost


if __name__ == '__main__':
    player = Player()
    player.loop()