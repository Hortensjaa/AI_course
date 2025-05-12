#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# 0 - lowercase player
# 1 - uppercase player
# !/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Customowy losowy agent do Dżungli, przechowujący stand gry w słownikach
Żeby przypadkiem za łatwo nie było go debugować nie XD
'''

import random
import sys


class Jungle:
    MX = 7
    MY = 9
    TRAPS = {(2, 0), (4, 0), (3, 1), (2, 8), (4, 8), (3, 7)}
    WATER = {(x, y) for x in [1, 2, 4, 5] for y in [3, 4, 5]}
    DENS = {0: (3, 8), 1: (3, 0)}
    DIRS = [(0, 1), (1, 0), (-1, 0), (0, -1)]
    SUPERIORITY = {
        'r': 0, 'c': 1, 'd': 2, 'w': 3, 'j': 4, 't': 5, 'l': 6, 'e': 7,
        'R': 0, 'C': 1, 'D': 2, 'W': 3, 'J': 4, 'T': 5, 'L': 6, 'E': 7
    }

    def __init__(self):
        self.pieces = {0 : {"animals": {}, "positions": {}}, 1: {"animals": {}, "positions": {}}}
        self._initialize_pieces()

    def _initialize_pieces(self):
        board = [
            "L.....T",
            ".D...C.",
            "R.J.W.E",
            ".......",
            ".......",
            ".......",
            "e.w.j.r",
            ".c...d.",
            "t.....l"
        ]
        for r in range(self.MY):
            for c in range(self.MX):
                piece = board[r][c]
                if piece == '.':
                    continue
                if piece.islower():
                    self.pieces[0]["animals"][piece] = (c, r)
                    self.pieces[0]["positions"][(c, r)] = piece
                else:
                    self.pieces[1]["animals"][piece] = (c, r)
                    self.pieces[1]["positions"][(c, r)] = piece

    def _get_animal(self, c, r, player) -> str | None:
        if (c, r) in self.pieces[player]["positions"]:
            return self.pieces[player]["positions"][(c, r)]
        return None

    def _get_position(self, animal, player) -> (int, int):
        if animal in self.pieces[player]["animals"]:
            return self.pieces[player]["animals"][animal]
        return None

    def _can_attack(self, start: (int, int), end: (int, int), attacker: str, defender: str, player: int) -> bool:
        assert attacker is not None
        assert defender is not None
        # move to occupied square - cant be self piece
        if defender in self.pieces[player]["animals"]:
            return False
        # logic of fight
        defender_in_trap = end in self.TRAPS
        attacker_is_rat = attacker in "Rr"
        defender_is_rat = defender in "Rr"
        attacker_is_elephant = attacker in "eE"
        defender_is_elephant = defender in "eE"
        rat_move_from_water = attacker_is_rat and start in self.WATER
        # basic case
        if not defender_in_trap and not attacker_is_rat and not defender_is_rat:
            if self.SUPERIORITY[attacker] >= self.SUPERIORITY[defender]:
                return True
        # przeciwnik w pułapce może być zawsze zbity oprócz ruchu szczura z wody
        if defender_in_trap and not rat_move_from_water:
            return True
        # jak szczur wyłazi z wody, to nie bije
        if rat_move_from_water:
            return False
        # szczur atakuje słonia git
        if attacker_is_rat and defender_is_elephant:
            return True
        # słoń atakuje szczura nie git
        if attacker_is_elephant and defender_is_rat:
            return False
        # szczur atakuje szczura chyba spoko?
        if attacker_is_rat and defender_is_rat:
            return True
        # szczur ze zwykłym ziomkiem
        return self.SUPERIORITY[attacker] >= self.SUPERIORITY[defender]

    # moves logic
    def _generate_moves_for_piece(self, start: (int, int), player: int) -> list:
        c, r = start
        moves = []
        attacker = self._get_animal(c, r, player)
        assert attacker is not None
        for dc, dr in self.DIRS:
            c2 = c + dc
            r2 = r + dr
            defender = self._get_animal(c2, r2, 1-player)
            if defender is None:
                defender = self._get_animal(c2, r2, player)
            # not outside the board
            if 0 <= c2 < self.MX and 0 <= r2 < self.MY:
                # not in the water
                if (c2, r2) not in self.WATER:
                    # not in self den
                    if (c2, r2) != self.DENS[player]:
                        # move to empty square
                        if defender is None:
                            moves.append((c2, r2))
                        # move to occupied square
                        elif self._can_attack(start, (c2, r2), attacker, defender, player):
                            moves.append((c2, r2))

                # big kitties jump
                if attacker in "lLtT":
                    for dc, dr in self.DIRS:
                        c2, r2 = c, r
                        valid_jump = False

                        while True:
                            c2 += dc
                            r2 += dr
                            if not (0 <= c2 < self.MX and 0 <= r2 < self.MY):
                                break
                            if (c2, r2) not in self.WATER:
                                valid_jump = True
                                break  # reached land
                            # check if any rat is blocking the jump
                            rat_block = self._get_animal(c2, r2, player)
                            if rat_block is not None:
                                rat_block = self._get_animal(c2, r2, 1-player)
                            if rat_block and rat_block.lower() == 'r':
                                break  # jump blocked by some rat

                        # if we reached land square
                        if not valid_jump:
                            continue  # jump ended in water, invalid
                        if (c2, r2) == self.DENS[player]:
                            continue  # cannot enter own den

                        defender = self._get_animal(c2, r2, 1 - player)
                        if defender is None:
                            defender = self._get_animal(c2, r2, player)
                        if defender is None:
                            moves.append((c2, r2))
                        elif self._can_attack((c, r), (c2, r2), attacker, defender, player):
                            moves.append((c2, r2))
        return moves

    def generate_all_moves(self, player: int) -> ((int, int), (int, int)):
        moves = []
        for c, r in self.pieces[player]["positions"]:
            piece_moves = self._generate_moves_for_piece((c, r), player)
            for move in piece_moves:
                moves.append(((c, r), move))
        return moves

    def do_move(self, start: (int, int), end: (int, int), player: int):
        # "invalid" move (not possible or sth)
        if -1 in start or -1 in end:
            return
        # assuming the move is valid
        c, r = start
        c2, r2 = end
        # move animal
        v = self.pieces[player]["positions"].pop((c, r))
        self.pieces[player]["positions"][(c2, r2)] = v
        self.pieces[player]["animals"][v] = (c2, r2)
        # remove defender
        d = self.pieces[1-player]["positions"].pop((c2, r2), None)
        if d is not None:
            self.pieces[1-player]["animals"].pop(d)

    def get_winner(self):
        if len(self.pieces[0]["animals"]) == 0:
            return 1
        elif len(self.pieces[1]["animals"]) == 0:
            return 0
        if self.DENS[0] in self.pieces[1]["positions"]:
            return 1
        if self.DENS[1] in self.pieces[0]["positions"]:
            return 0
        return None


class Player(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.game = Jungle()
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

            moves = self.game.generate_all_moves(self.my_player)
            if moves:
                move = random.choice(moves)
                self.game.do_move(move[0], move[1], self.my_player)
                move = (move[0][0], move[0][1], move[1][0], move[1][1])
            else:
                move = (-1, -1, -1, -1)
            self.say('IDO %d %d %d %d' % move)


if __name__ == '__main__':
    player = Player()
    player.loop()

