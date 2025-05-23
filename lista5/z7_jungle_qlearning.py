
'''
Customowy losowy agent do Dżungli, przechowujący stand gry w słownikach
Żeby przypadkiem za łatwo nie było go debugować nie XD
# 0 - lowercase player
# 1 - uppercase player
'''

import random

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

    ALPHA = 0.001
    GAMMA = 0.99
    EPSILON_DECAY = 0.99
    MAX_SUM_PIECE_VALUES = sum(PIECE_VALUES.values()) // 2
    MAX_DISTANCE = abs(3 - 0) + abs(8 - 0)
    MAX_SUM_DISTANCE = MAX_DISTANCE * MX

    def __init__(self):
        self.pieces = {0 : {"animals": {}, "positions": {}}, 1: {"animals": {}, "positions": {}}}
        self._initialize_pieces()
        # q learning agent
        self.weights = {
            "values_sum_diff": 0.0, "sum_distance_diff": 0.0, "closest_piece_diff": 0.0,  # state before move
            "distance_progress": 0.0, "captured_piece_value": 0.0  # action taken
        }
        self.history: list[tuple[tuple[int, int], tuple[int, int], int]] = []  # (start, end, player)
        self.epsilon = 1.0  # exploration rate

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

    def print_gamestate(self):
        board = [["." for _ in range(self.MX)] for _ in range(self.MY)]
        for player_id, data in self.pieces.items():
            for (x, y), piece in data["positions"].items():
                board[y][x] = piece
        print("Current Game State:")
        for row in board:
            print("".join(row))

    def _get_animal(self, c, r, player) -> str | None:
        if (c, r) in self.pieces[player]["positions"]:
            return self.pieces[player]["positions"][(c, r)]
        return None

    def _get_position(self, animal, player) -> tuple[int, int]:
        if animal in self.pieces[player]["animals"]:
            return self.pieces[player]["animals"][animal]
        return None

    def _can_attack(self, start: tuple[int, int], end: tuple[int, int], attacker: str, defender: str, player: int) -> bool:
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

    def _generate_moves_for_piece(self, start: tuple[int, int], player: int) -> list:
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

    def generate_all_moves(self, player: int) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        moves = []
        for c, r in self.pieces[player]["positions"]:
            piece_moves = self._generate_moves_for_piece((c, r), player)
            for move in piece_moves:
                moves.append(((c, r), move))
        return moves

    def do_move(self, start: tuple[int, int], end: tuple[int, int], player: int):
        if -1 in start or -1 in end:
            return None

        c, r = start
        c2, r2 = end

        v = self.pieces[player]["positions"].pop((c, r))
        self.pieces[player]["positions"][(c2, r2)] = v
        self.pieces[player]["animals"][v] = (c2, r2)

        captured = self.pieces[1 - player]["positions"].pop((c2, r2), None)
        if captured is not None:
            self.pieces[1 - player]["animals"].pop(captured)

        return {
            "player": player,
            "start": start,
            "end": end,
            "moved_piece": v,
            "captured_piece": captured
        }

    def undo_move(self, move_data: dict):
        player = move_data["player"]
        start = move_data["start"]
        end = move_data["end"]
        v = move_data["moved_piece"]
        captured = move_data["captured_piece"]

        self.pieces[player]["positions"].pop(end)
        self.pieces[player]["positions"][start] = v
        self.pieces[player]["animals"][v] = start

        if captured is not None:
            self.pieces[1 - player]["positions"][end] = captured
            self.pieces[1 - player]["animals"][captured] = end

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

    def reset(self):
        self.pieces = {0 : {"animals": {}, "positions": {}}, 1: {"animals": {}, "positions": {}}}
        self._initialize_pieces()
        self.history: list[tuple[tuple[int, int], tuple[int, int], int]] = []

    @staticmethod
    def _distance(p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # ----------------- a) random agent -----------------
    def random_agent_move(self, player: int):
        moves = self.generate_all_moves(player)
        if not moves:
            self.history.append(((-1, -1), (-1, -1), player))
            return
        start, end = random.choice(moves)
        self.do_move(start, end, player)
        self.history.append((start, end, player))

    # ----------------- b) greedy agent -----------------
    def greedy_agent_move(self, player: int):
        moves = self.generate_all_moves(player)
        if not moves:
            self.history.append(((-1, -1), (-1, -1), player))
            return

        r = random.random()  # flip a coin

        if r < 0.5:
            self.random_agent_move(player)
        else:
            target_den = self.DENS[1 - player]

            best_move = None
            best_distance = float('inf')

            for start, end in moves:
                distance = self._distance(end, target_den)
                if distance < best_distance:
                    best_distance = distance
                    best_move = (start, end)

            if best_move:
                start, end = best_move
                self.do_move(start, end, player)
                self.history.append((start, end, player))

    # ----------------- c) q learning agent -----------------
    def _values_sum_diff(self, player: int):
        my_value = sum(self.PIECE_VALUES[p] for p in self.pieces[player]["animals"].keys())
        opp_value = sum(self.PIECE_VALUES[p] for p in self.pieces[1 - player]["animals"].keys())
        return my_value - opp_value

    def _sum_distance_diff(self, player: int):
        my_pieces = self.pieces[player]["positions"]
        opp_pieces = self.pieces[1 - player]["positions"]
        my_den = self.DENS[1 - player]
        opp_den = self.DENS[player]
        my_sum_dist = sum(self._distance(pos, my_den) for pos in my_pieces)
        opp_sum_dist = sum(self._distance(pos, opp_den) for pos in opp_pieces)
        return my_sum_dist - opp_sum_dist

    def _closest_piece_diff(self, player: int):
        my_pieces = self.pieces[player]["positions"]
        opp_pieces = self.pieces[1 - player]["positions"]
        my_den = self.DENS[1 - player]
        opp_den = self.DENS[player]
        my_closest = min((self._distance(pos, my_den) for pos in my_pieces), default=100)
        opp_closest = min((self._distance(pos, opp_den) for pos in opp_pieces), default=100)
        return my_closest - opp_closest

    # extract features (quality of state + action)
    def _extract_features(self, move_data: dict, player: int) -> dict[str, float]:
        return {
            "values_sum_diff": self._values_sum_diff(player) / self.MAX_SUM_PIECE_VALUES,
            "sum_distance_diff": self._sum_distance_diff(player) / self.MAX_SUM_DISTANCE,
            "closest_piece_diff": self._closest_piece_diff(player) / self.MAX_DISTANCE,
            "distance_progress": (self._distance(move_data["end"], self.DENS[1 - player]) -
                                  self._distance(move_data["start"], self.DENS[1 - player])) / self.MAX_DISTANCE,
            "captured_piece_value": (self.PIECE_VALUES.get(move_data["captured_piece"], 0) / self.MAX_SUM_PIECE_VALUES)
        }

    def _dot_product(self, features: dict[str, float]) -> float:
        return sum(self.weights[k] * features.get(k, 0.0) for k in self.weights)

    # Q(s,a) = wT ⋅ ϕ(s,a)
    # δ = r + γ ⋅ max(Q(s'',a'')) − Q(s,a)
    # w := w + α ⋅ δ ⋅ ϕ(s,a)
    def _update_weights(self, features_before: dict[str, float], best_features_after: dict[str, float], reward: int):
        for k in self.weights:
            td_error = reward + self.GAMMA * self._dot_product(best_features_after) - self._dot_product(features_before)  # δ
            update = self.ALPHA * td_error * features_before[k]  # α ⋅ δ ⋅ ϕ(s,a)
            self.weights[k] += update
            self.weights[k] = round(self.weights[k], 5)

    # update agents knowledge after the end of the game
    def update_knowledge(self, player: int):
        winner = self.get_winner()
        if winner is None:
            return

        reward = 1 if winner == player else -1

        # simulate whole game and update weights
        self.pieces = {0: {"animals": {}, "positions": {}}, 1: {"animals": {}, "positions": {}}}
        self._initialize_pieces()

        self.history.reverse()

        while self.history:
            # simulate my move to calculate Q(s,a)
            start, end, player = self.history.pop()
            m = self.do_move(start, end, player)
            self.undo_move(m)
            features_before = self._extract_features(m, player)
            # do my move
            m = self.do_move(start, end, player)

            # simulate opponent move
            start, end, player = self.history.pop()
            self.do_move(start, end, player)

            # simulate my possible moves to get Q(s'', a'')
            player = 1 - player
            possible_moves = self.generate_all_moves(player)
            best_features_after = None
            best_value = float('-inf')

            for move in possible_moves:
                m2 = self.do_move(move[0], move[1], player)
                features = self._extract_features(m2, player)
                value = self._dot_product(features)
                self.undo_move(m2)

                if value > best_value:
                    best_value = value
                    best_features_after = features

            # update
            self._update_weights(features_before, best_features_after, reward)

    def qlearning_agent_move(self, player: int):
        best_value = float('-inf')
        best_move = ((-1, -1), (-1, -1))

        r = random.random()

        if r < self.epsilon:
            self.random_agent_move(player)
            return

        for start, end in self.generate_all_moves(player):
            m = self.do_move(start, end, player)
            features = self._extract_features(m, player)
            value = self._dot_product(features)
            if value > best_value:
                best_value = value
                best_move = (start, end)
            self.undo_move(m)

        self.do_move(best_move[0], best_move[1], player)
        self.history.append((best_move[0], best_move[1], player))


if __name__ == "__main__":
    j = Jungle()
    wins = 0
    lost = []
    for i in range(1000):
        while j.get_winner() is None:
            # j.print_gamestate()
            j.qlearning_agent_move(0)
            j.greedy_agent_move(1)
            j.epsilon *= j.EPSILON_DECAY
        if j.get_winner() == 0:
            wins += 1
        else:
            lost.append(i)
        print("the winner is: ", j.get_winner())
        j.update_knowledge(0)
        j.reset()

    print("take a look at the weights: ", j.weights)
    print("all wins: ", wins)
    print("lost parties: ", lost)

