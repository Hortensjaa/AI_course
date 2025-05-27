import random
from collections import deque
from typing import List, Tuple, Set


class CommandoSolver:

    def __init__(self, maze: List[str]):
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0])

        self.start_points = self._find_start_points()
        self.goal_points = self._find_goal_points()
        self.possible_positions = set(self.start_points)


    def _find_start_points(self) -> List[Tuple[int, int]]:
        result = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] == "S" or self.maze[i][j] == "B":
                    result.append((i, j))
        return result

    def _find_goal_points(self) -> List[Tuple[int, int]]:
        result = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] == "G" or self.maze[i][j] == "B":
                    result.append((i, j))
        return result

    def _is_valid_move(self, r: int, c: int) -> bool:
        if (0 <= r < self.rows and
            0 <= c < self.cols and
            self.maze[r][c] != "#"):
            return True
        return False


    # redukcja niepewności
    def reduce_uncertainty_phase(self, max_moves: int = 150, look_ahead: int = 2):
        memo = {}
        moves = []
        positions = set(self.start_points)
        directions = [("U", -1, 0), ("D", 1, 0), ("L", 0, -1), ("R", 0, 1)]

        # print(f"Początkowa niepewność: {len(positions)} pozycji")

        # szybkie zakończenie, jeśli już mamy maksymalnie 3 pozycje
        if len(positions) <= 3:
            # print(f"Już osiągnięto docelową niepewność ({len(positions)} pozycji)")
            return moves, next(iter(positions))

        for i in range(max_moves):
            # sprawdzamy wszystkie kierunki i bierzemy najlepszy
            best_dir = None
            best_positions_count = len(positions)
            best_new_positions = None

            for move_dir, dr, dc in directions:
                new_positions = set()

                # Oblicz nowe pozycje dla tego kierunku
                for r, c in positions:
                    new_r, new_c = r + dr, c + dc
                    if self._is_valid_move(new_r, new_c):
                        new_positions.add((new_r, new_c))
                    else:
                        new_positions.add((r, c))

                # Wybierz kierunek dający najmniejszą liczbę pozycji
                if len(new_positions) < best_positions_count:
                    best_positions_count = len(new_positions)
                    best_dir = move_dir
                    best_new_positions = new_positions

            # Jeśli żaden kierunek nie redukuje, spróbuj spojrzeć dalej
            if best_dir is None and look_ahead > 1:
                best_sequence = self._look_ahead_reduction(positions, look_ahead, memo=memo)
                if best_sequence:
                    best_dir, best_new_positions = best_sequence[0]
                else:
                    # Jeśli nadal nie znaleziono, wybierz kierunek losowo
                    move_dir, dr, dc = random.choice(directions)
                    best_dir = move_dir
                    best_new_positions = set()
                    for r, c in positions:
                        new_r, new_c = r + dr, c + dc
                        if self._is_valid_move(new_r, new_c):
                            best_new_positions.add((new_r, new_c))
                        else:
                            best_new_positions.add((r, c))

            # Wykonaj ruch
            moves.append(best_dir)
            positions = best_new_positions
            # print(f"Ruch {i + 1}: {best_dir} - Pozostało pozycji: {len(positions)}")

            # Warunek zakończenia - osiągnięto maksymalnie 3 pozycje
            if len(positions) <= 3:
                # print(f"Osiągnięto docelową niepewność ({len(positions)} pozycji)!")
                break

        # print(f"Końcowa niepewność: {len(positions)} pozycji po {len(moves)} ruchach")

        # Wyświetl planszę wynikową
        # self._display_result_board(positions)

        return moves, next(iter(positions)) if positions else None

    def _display_result_board(self, positions):
        """Wyświetla planszę wynikową z pozycjami komandosów i celów."""
        result_board = [['.' for _ in range(self.cols)] for _ in range(self.rows)]

        # Dodaj ściany do planszy wynikowej
        for r in range(self.rows):
            for c in range(self.cols):
                if self.maze[r][c] == "#":
                    result_board[r][c] = "#"

        # Dodaj punkty celu do planszy wynikowej
        for r, c in self.goal_points:
            result_board[r][c] = "G"

        # Oznacz zredukowane pozycje
        for r, c in positions:
            result_board[r][c] = "C"

        print("\nPlansza wynikowa po fazie redukcji:")
        for row in result_board:
            print("".join(row))

    # szukanie sekwencji ruchów (czyli nie patrzymy na pojedynczy ruch, tylko od razu na 2)
    def _look_ahead_reduction(self, positions: Set[Tuple[int, int]], depth: int = 2, memo=None):

        if memo is None:
            memo = {}

        positions_key = tuple(sorted(positions))
        if (positions_key, depth) in memo:
            return memo[(positions_key, depth)]

        if depth <= 0:
            return None

        directions = [("U", -1, 0), ("D", 1, 0), ("L", 0, -1), ("R", 0, 1)]
        best_sequence = None
        best_reduction = 0

        for move_dir, dr, dc in directions:
            new_positions = set()
            for r, c in positions:
                new_r, new_c = r + dr, c + dc
                if self._is_valid_move(new_r, new_c):
                    new_positions.add((new_r, new_c))
                else:
                    new_positions.add((r, c))

            reduction = len(positions) - len(new_positions)

            if reduction > 0:
                return [(move_dir, new_positions)]

            # Rekurencyjnie sprawdź następny poziom
            next_sequence = self._look_ahead_reduction(new_positions, depth - 1)
            if next_sequence:
                total_reduction = len(positions) - len(next_sequence[-1][1])
                if total_reduction > best_reduction:
                    best_reduction = total_reduction
                    best_sequence = [(move_dir, new_positions)] + next_sequence

        memo[(positions_key, depth)] = best_sequence
        return best_sequence


    def find_path_to_goal(self, commando_pos: set[Tuple[int, int]]) -> List[str]:
        from collections import deque

        queue = deque([(commando_pos, [])])
        visited = {tuple(sorted(commando_pos))}
        directions = [("U", -1, 0), ("D", 1, 0), ("L", 0, -1), ("R", 0, 1)]
        max_path = 150  # limit ścieżki

        goal_points_set = set(self.goal_points)

        while queue:
            current_positions, path = queue.popleft()

            if len(path) >= max_path:
                continue

            # warunek końcowy
            if all(pos in goal_points_set for pos in current_positions):
                return path

            # ruch w każdym kierunku
            for dir_name, dr, dc in directions:
                new_positions = set()

                # ... każdego komandosa
                for r, c in current_positions:
                    new_r, new_c = r + dr, c + dc
                    if self._is_valid_move(new_r, new_c):
                        new_positions.add((new_r, new_c))
                    else:
                        new_positions.add((r, c))

                if new_positions == current_positions:
                    continue

                # sprawdzamy czy stan nie wystąpił wcześniej
                new_state = tuple(sorted(new_positions))
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_positions, path + [dir_name]))

        return []

    def solve(self) -> str:
        # faza 1: redukcja niepewności
        reduction_moves, _ = self.reduce_uncertainty_phase(
            max_moves=150,
            # no_improvement_count=140,
            # random_treshhold=0.6
        )

        current_positions = set()

        dir_offsets = {
            "U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)
        }

        # wykonuję pozycje dążące do redukcji
        for start in self.start_points:
            pos = start
            for move in reduction_moves:
                dr, dc = dir_offsets[move]
                new_r, new_c = pos[0] + dr, pos[1] + dc
                if self._is_valid_move(new_r, new_c):
                    pos = (new_r, new_c)
            current_positions.add(pos)

        # Faza 2: bfs
        path_to_goal = self.find_path_to_goal(current_positions)

        if len(reduction_moves) + len(path_to_goal) > 150:
            reduction_moves, _ = self.reduce_uncertainty_phase(max_moves=15)

            current_positions = set()
            for start in self.start_points:
                pos = start
                for move in reduction_moves:
                    dr, dc = dir_offsets[move]
                    new_r, new_c = pos[0] + dr, pos[1] + dc
                    if self._is_valid_move(new_r, new_c):
                        pos = (new_r, new_c)
                current_positions.add(pos)

            path_to_goal = self.find_path_to_goal(current_positions)

        # Połączenie pozycji w 1 ścieżkę (dojście do redukcji + szukanie celu)
        return "".join(reduction_moves + path_to_goal)

