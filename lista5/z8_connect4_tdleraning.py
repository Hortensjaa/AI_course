from random import choice, random

import numpy as np

# 0 - player 0
# 1 - player 1
class Connect4:
    COLS_NUM = 7
    ROWS_NUM = 6

    ALPHA = 0.1  # learning rate
    GAMMA = 0.99 # discount factor
    EPSILON_DECAY = 0.99

    def __init__(self, epsilon: float = 1):
        self.board = [[None] * self.COLS_NUM for _ in range(self.ROWS_NUM)]
        self.epsilon = epsilon
        self.td_table = {}
        self.history = []

    # player adds a piece to the column
    def move(self, col: int, player: int):
        for row in range(0, self.ROWS_NUM):
            if self.board[row][col] is None:
                self.board[row][col] = player
                return row, col
        raise ValueError("Column is full")

    # terminal state -> player who won
    def is_terminal(self) -> int | None:
        for row in range(self.ROWS_NUM):
            for col in range(self.COLS_NUM):
                player = self.board[row][col]
                if player is None:
                    continue
                # horizontal →
                if col <= self.COLS_NUM - 4:
                    if all(self.board[row][col + i] == player for i in range(4)):
                        return player
                # vertical ↓
                if row <= self.ROWS_NUM - 4:
                    if all(self.board[row + i][col] == player for i in range(4)):
                        return player
                # left diagonal ↘
                if row <= self.ROWS_NUM - 4 and col <= self.COLS_NUM - 4:
                    if all(self.board[row + i][col + i] == player for i in range(4)):
                        return player
                # right diagonal ↗
                if row >= 3 and col <= self.COLS_NUM - 4:
                    if all(self.board[row - i][col + i] == player for i in range(4)):
                        return player
        # draw
        if all(cell is not None for row in self.board for cell in row):
            return -1
        return None

    def print_board(self):
        symbols = {None: ".", 0: "X", 1: "O"}
        for row in reversed(self.board):
            print(" ".join(symbols[cell] for cell in row))
        print("0 1 2 3 4 5 6\n")

    def all_possible_moves(self):
        return [col for col in range(self.COLS_NUM)
                if self.board[self.ROWS_NUM - 1][col] is None]

    def reset_game(self):
        self.board = [[None] * self.COLS_NUM for _ in range(self.ROWS_NUM)]
        self.history = []
        self.epsilon *= self.EPSILON_DECAY  # decay after every episode

    # ------ random agent -------
    def random_agent_move(self, player: int):
        valid_cols = self.all_possible_moves()
        self.move(choice(valid_cols), player)

    # ------ td learning agent -------
    def serialize(self):
        return tuple(tuple(row) for row in self.board)

    # choosing moves in agent
    def td_agent_move(self, player: int):
        # remember the last state
        state = self.serialize()
        self.td_table.setdefault(state, 0)

        # choose the best from valid states OR random (depending on epsilon)
        possible_moves = self.all_possible_moves()
        if random() < self.epsilon:
            chosen_col = choice(possible_moves)
        else:
            best_value = -float('inf')
            best_move = None
            for col in possible_moves:
                # move
                row, _ = self.move(col, player)
                next_state = self.serialize()
                value = self.td_table.get(next_state, 0.0)
                # undo
                self.board[row][col] = None
                # find the best move
                if value > best_value:
                    best_value = value
                    best_move = col
            chosen_col = best_move

        # actually do the chosen move
        self.move(chosen_col, player)

    # when state is terminal, I need to update the td table
    def update_td_table(self, reward: float):
        target = reward
        for state in reversed(self.history):
            old_value = self.td_table.get(state, 0.0)
            new_value = old_value + self.ALPHA * (target - old_value)
            self.td_table[state] = new_value
            target = new_value * self.GAMMA


"""
Result: td learning agent after about 1000 games reach an stable point of ~80% win rate with random agent
"""
if __name__ == "__main__":
    game = Connect4()

    td_player = 0
    random_player = 1

    td_wins = 0
    for i in range(1, 5001):
        while game.is_terminal() is None:
            game.td_agent_move(td_player)
            game.random_agent_move(random_player)

        rew = game.is_terminal()
        if rew == td_player:
            game.update_td_table(1)
            td_wins += 1
            # print(f"Player {td_player} wins")
        elif rew == random_player:
            game.update_td_table(0)
            # print(f"Player {random_player} wins")
        else:
            game.update_td_table(0.5)
            # print(f"DRAW")

        if i % 50 == 0:
            print(f"After {i} games, TD agent won {td_wins} times in last 50 games ({(td_wins / 50) * 100:.1f}%)")
            td_wins = 0

        game.reset_game()







