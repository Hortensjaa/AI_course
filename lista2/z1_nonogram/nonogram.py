from random import random, choice, randint
from time import time

from lista2.z1.utils import calculate_line_score, str_cell, calculate_guaranteed_cells


# {0: pusta, 1: pełna, 2: gwarantowana}

class Nonogram:
    def __init__(self, row_definitions: [int], col_definitions: [int]):
        self.row_defs = row_definitions
        self.col_defs = col_definitions
        self.height = len(row_definitions)
        self.width = len(col_definitions)
        self.current_score = 0
        self.best_grid = None
        self.row_scores = [0] * self.height
        self.col_scores = [0] * self.width
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.rows_combinations = []
        self.cols_combinations = []
        self.reset_grid()

    def set_cell(self, row: int, col: int, value: int):
        self.grid[row][col] = value

    def get_row(self, row_num: int):
        return self.grid[row_num]

    def get_col(self, col_num: int):
        return [self.grid[i][col_num] for i in range(self.height)]

    def set_row(self, row_num: int, new_row_value: [int]):
        for i in range(self.width):
            self.grid[row_num][i] = new_row_value[i]

    def set_col(self, col_num: int, new_col_value: [int]):
        for i in range(self.height):
            self.grid[i][col_num] = new_col_value[i]

    def display(self):
        max_row_len = max(len(row) for row in self.row_defs)
        max_col_len = max(len(col) for col in self.col_defs)

        col_headers = list(map(lambda col: [str(n) for n in col], self.col_defs))
        for col in col_headers:
            while len(col) < max_col_len:
                col.insert(0, " ")
        col_headers = list(map(list, zip(*col_headers)))

        row_headers = [" ".join(map(str, row)).rjust(max_row_len * 2) for row in self.row_defs]

        board_rows = [" ".join(map(str_cell, row)) for row in self.grid]

        col_header_str = "\n".join(" " * (max_row_len * 2 + 1) + " ".join(row) for row in col_headers)
        board_str = "\n".join(f"{row_headers[i]} {board_rows[i]}" for i in range(self.height))

        return f"{col_header_str}\n{board_str}"

    def calculate_initial_board_score(self):
        for r in range(self.height):
            self.row_scores[r] = calculate_line_score(self.get_row(r), self.row_defs[r], self.rows_combinations[r])
        for c in range(self.width):
            self.col_scores[c] = calculate_line_score(self.get_col(c), self.col_defs[c], self.cols_combinations[c])
        total_score = sum(self.row_scores) + sum(self.col_scores)
        self.current_score = total_score

    def is_solved(self):
        return self.current_score == 2 * self.height * self.width

    def get_invalid_lines(self):
        invalid_rows = []
        for r in range(self.height):
            if self.row_scores[r] != self.width:
                invalid_rows.append(r)

        invalid_cols = []
        for c in range(self.width):
            if self.col_scores[c] != self.height:
                invalid_cols.append(c)

        return invalid_rows, invalid_cols

    def reset_grid(self):
        for i in range(len(self.col_defs)):
            r, c = calculate_guaranteed_cells(self.col_defs[i], self.height)
            self.set_col(i, r)
            self.cols_combinations.append(c)
        for j in range(len(self.row_defs)):
            guaranteed, c = calculate_guaranteed_cells(self.row_defs[j], self.width)
            self.rows_combinations.append(c)
            for i in range(self.width):
                if guaranteed[i] == 2:
                    self.grid[j][i] = 2
        self.calculate_initial_board_score()

    def neg_cell_score(self, row_index: int, col_index: int) -> tuple[int, int, int]:
        if self.grid[row_index][col_index] < 2:
            self.grid[row_index][col_index] = 1 - self.grid[row_index][col_index]

            new_row_score = calculate_line_score(self.get_row(row_index), self.row_defs[row_index], self.rows_combinations[row_index])
            new_col_score = calculate_line_score(self.get_col(col_index), self.col_defs[col_index], self.cols_combinations[col_index])

            self.grid[row_index][col_index] = 1 - self.grid[row_index][col_index]

            return ((new_row_score + new_col_score) - (self.row_scores[row_index] + self.col_scores[col_index]),
                    new_row_score, new_col_score)
        return 0, self.row_scores[row_index], self.col_scores[col_index]

    def solve(self, timeout=120, restart_after=100, random_change=0.01):
        max_iterations = self.width * self.height * 30
        start_time = time()
        best_score = float('-inf')
        iterations_since_improvement = 0

        iteration = 0
        while True:
            # jeśli sprawdzona, to kończymy
            if self.is_solved():
                return True

            iteration += 1
            if iteration > max_iterations:
                return self.solve()

            # liczymy iteracje od ostatniej poprawy, zeby wiedzieć, kiedy utkniemy
            if self.current_score > best_score:
                best_score = self.current_score
                self.best_grid = [row[:] for row in self.grid]
                iterations_since_improvement = 0
            else:
                iterations_since_improvement += 1

            # ... wtedy restart
            if iterations_since_improvement > restart_after:
                self.reset_grid()
                iterations_since_improvement = 0
                continue

            # niepoprawne linie - zarówno wiersze, jak i kolumny
            invalid_rows, invalid_cols = self.get_invalid_lines()

            rand = random()
            # wybieramy wiersz do zmiany...
            if invalid_rows and (not invalid_cols or rand > 0.5):
                row_index = choice(invalid_rows)
                best_improvement = float('-inf')
                candidates = []

                for col in range(self.width):
                    improvement, row_score, col_score = self.neg_cell_score(row_index, col)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        candidates = [(col, row_score, col_score)]
                    elif improvement == best_improvement:
                        candidates.append((col, row_score, col_score))

                col_index, new_row_score, new_col_score = choice(candidates)

            # ... albo kolumnę
            elif rand > random_change:
                col_index = choice(invalid_cols)
                best_improvement = float('-inf')
                candidates = []

                for row in range(self.height):
                    improvement, row_score, col_score = self.neg_cell_score(row, col_index)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        candidates = [(row, row_score, col_score)]
                    elif improvement == best_improvement:
                        candidates.append((row, row_score, col_score))

                row_index, new_row_score, new_col_score = choice(candidates)

            else:
                row_index = randint(0, self.height-1)
                col_index = randint(0, self.width-1)
                best_improvement, new_row_score, new_col_score = self.neg_cell_score(row_index, col_index)

            # negujemy wybraną komórkę
            if self.grid[row_index][col_index] < 2:
                self.grid[row_index][col_index] = 1 - self.grid[row_index][col_index]

            # aktualizujemy score
            # print(f"Changing: {row_index, col_index}, old scores: {self.row_scores[row_index], self.col_scores[col_index]}, new scores: {new_row_score, new_col_score}, improvement: {best_improvement}")
            self.current_score += best_improvement
            self.row_scores[row_index] = new_row_score
            self.col_scores[col_index] = new_col_score

        if self.best_grid and not self.is_solved():
            self.grid = self.best_grid

        return self.is_solved()



