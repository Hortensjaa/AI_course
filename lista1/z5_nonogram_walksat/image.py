from random import random, choice
from time import time
from utils import check_line_quality, is_line_valid


class Image:
    def __init__(self, rows: [int], cols: [int], x: int, y: int):
        # specyfikacja
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        # stan
        self.best_score = float('-inf')
        self.best_grid = None
        self.grid = []
        self.current_score = 0
        self.reset_grid()

    def reset_grid(self):
        self.grid = [[0 for _ in range(self.x)] for _ in range(self.y)]
        self.current_score = self.calculate_total_score()

    def calculate_row_score(self, row_index):
        row = self.grid[row_index]
        return check_line_quality(row, self.rows[row_index])

    def calculate_col_score(self, col_index):
        col = [self.grid[row][col_index] for row in range(self.y)]
        return check_line_quality(col, self.cols[col_index])

    def calculate_total_score(self):
        row_scores = sum(self.calculate_row_score(r) for r in range(self.y))
        col_scores = sum(self.calculate_col_score(c) for c in range(self.x))
        return row_scores + col_scores

    def is_solved(self):
        for r in range(self.y):
            if not is_line_valid(self.grid[r], self.rows[r]):
                return False

        for c in range(self.x):
            column = [self.grid[r][c] for r in range(self.y)]
            if not is_line_valid(column, self.cols[c]):
                return False
        return True

    # obliczamy, czy odwrócenie komórki wychodzi nam na +
    def neg_cell_score(self, row_index, col_index):
        old_row_score = self.calculate_row_score(row_index)
        old_col_score = self.calculate_col_score(col_index)

        self.grid[row_index][col_index] = 1 - self.grid[row_index][col_index]

        new_row_score = self.calculate_row_score(row_index)
        new_col_score = self.calculate_col_score(col_index)

        self.grid[row_index][col_index] = 1 - self.grid[row_index][col_index]

        return (new_row_score + new_col_score) - (old_row_score + old_col_score)

    def get_invalid_lines(self):
        invalid_rows = []
        for r in range(self.y):
            if not is_line_valid(self.grid[r], self.rows[r]):
                invalid_rows.append(r)

        invalid_cols = []
        for c in range(self.x):
            column = [self.grid[r][c] for r in range(self.y)]
            if not is_line_valid(column, self.cols[c]):
                invalid_cols.append(c)

        return invalid_rows, invalid_cols

    def solve(self, max_iterations=200000, timeout=10, restart_after=1000):
        start_time = time()
        best_score = float('-inf')
        iterations_since_improvement = 0

        iteration = 0
        while iteration < max_iterations and time() - start_time < timeout:
            iteration += 1

            # jeśli sprawdzona, to kończymy
            if self.is_solved():
                return True

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

            # wybieramy wiersz do zmiany...
            if invalid_rows and (not invalid_cols or random() < 0.5):
                row_index = choice(invalid_rows)
                best_cell = None
                best_improvement = float('-inf')

                for col in range(self.x):
                    improvement = self.neg_cell_score(row_index, col)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_cell = col

                col_index = best_cell

            # ... albo kolumnę
            else:
                col_index = choice(invalid_cols)
                best_cell = None
                best_improvement = float('-inf')

                for row in range(self.y):
                    improvement = self.neg_cell_score(row, col_index)
                    if improvement > best_improvement:
                        best_improvement = improvement
                        best_cell = row

                row_index = best_cell

            # negujemy wybraną komórkę
            self.grid[row_index][col_index] = 1 - self.grid[row_index][col_index]

            # aktualizujemy score
            self.current_score = self.calculate_total_score()

        if self.best_grid and not self.is_solved():
            self.grid = self.best_grid

        return self.is_solved()


