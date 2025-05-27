from random import choice

from solution_mcts import Reversi
from copy import deepcopy


"""
1 tura:
- selekcja: 
    na początku mam stan planszy z 4 pionkami (stan początkowy nie ma dzieci)
- expansion: 
    dodaję węzły ze wszystkimi możliwymi ruchami (albo kilkoma, jeśli to nie będzie się kalkulowało czasowo).
- symulacja: 
    z każdego z tych dzieci rozgrywam 1 losową symulację do końca. 
    To mi zbuduje takie drzewo ktore ma rozgalezienie tylko na gorze, a pozniej idzie prostymi sciezkami
- backpropagation: 
    przekazuję w górę liczbę wygranych gier (0, 0.5 albo 1 na tym poziomie - remis to pół zwycięstwa)
-- teraz czekam na ruch przeciwnika i na jego podstawie wchodzę do następnego węzła stanu

n-ta tura:
- rozważam możliwe ruchy, 
- symuluję rozgrywki z nich
- oceniam je 
- aktualizuję prawdopodobieństwa węzłów
"""


class MCTSNode:
    DRAW_SCORE = 0.6
    WEIGHTS = [
        [120, -20, 10, 5, 5, 10, -20, 120],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10, -2, -1, -1, -1, -1, -2, 10],
        [5, -2, -1, -1, -1, -1, -2, 5],
        [5, -2, -1, -1, -1, -1, -2, 5],
        [10, -2, -1, -1, -1, -1, -2, 10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [120, -20, 10, 5, 5, 10, -20, 120],
    ]

    def __init__(self, parent=None):
        # struktura
        self.children = {}  # klucze - ruchy prowadzące do nowego stanu
        self.parent = parent

        # zmieniające się parametry
        self.games_played = 0
        self.games_won = 0.0

    def winning_probability(self):
        return 0.0 if not self.games_played else self.games_won / self.games_played

    def select(self, game, exploration_param=1.44):
        import math

        current_player = len(game.move_list) % 2
        possible_moves = game.moves(current_player)

        # sprawdź, czy mamy nieodwiedzone ruchy (które nie są jeszcze w drzewie)
        unexplored_moves = [move for move in possible_moves if move not in self.children]
        # jeśli są nieodwiedzone ruchy (przechodzimy do ekspansji) lub nie ma możliwych ruchów, zwróć ten węzeł
        if unexplored_moves or not possible_moves:
            return self, []

        # Wybierz dziecko z najlepszym UCT
        best_score = -float('inf')
        best_move = None
        best_child = None

        for move, child in self.children.items():
            if child.games_played == 0:
                score = float('inf')
            else:
                exploitation = child.winning_probability()
                exploration = exploration_param * math.sqrt(math.log(self.games_played) / child.games_played)
                score = exploitation + exploration

            if score > best_score:
                best_score = score
                best_move = move
                best_child = child

        # wykonujemy ruch na kopii (później go cofnę)
        game.do_move(best_move, current_player)

        # rekurencyjnie wybieramy najlepsze dziecko
        selected_node, path = best_child.select(game, exploration_param)
        return selected_node, [best_move] + path

    def expand(self, game):
        current_player = len(game.move_list) % 2
        possible_moves = game.moves(current_player)

        # znajdź ruchy, które nie są jeszcze w drzewie
        unexplored_moves = [move for move in possible_moves if move not in self.children]
        assert len(unexplored_moves) > 0

        # wybieramy losowo ruch i wykonujemy go
        move = choice(unexplored_moves)
        game.do_move(move, current_player)

        # dodajemy do drzewka stan po nim
        child = MCTSNode(parent=self)
        self.children[move] = child

        return child

    def simulate(self, game, my_player):

        # Sprawdzamy, kto wykonuje ruch w tym węźle
        player_at_node = len(game.move_list) % 2

        # Symulujemy grę do końca
        current_player = player_at_node
        while not game.terminal():
            possible_moves = game.moves(current_player)

            if not possible_moves:
                game.do_move(None, current_player)
            else:
                move = max(possible_moves, key=lambda m: self.WEIGHTS[m[0]][m[1]])
                game.do_move(move, current_player)

            current_player = 1 - current_player

        final_result = game.result()

        if final_result == 0:
            return self.DRAW_SCORE
        elif (final_result > 0 and my_player == 1) or (final_result < 0 and my_player == 0):
            return 1.0
        else:
            return 0.0

    def evaluate(self, game, result):
        self.games_played += 1
        self.games_won += result
        game.undo_move()

        if self.parent:
            self.parent.evaluate(game, result)


