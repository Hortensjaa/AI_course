from random import choice, random

import numpy as np

# 0 - player 0
# 1 - player 1
class Connect4:
    COLS_NUM = 7
    ROWS_NUM = 6

    ALPHA = 0.01  # learning rate
    GAMMA = 0.99 # discount factor
    EPSILON_DECAY = 0.99

    FEATURE_COUNT = 6
    
    # Features:
    # 0: Bias term
    # 1: Number of pieces in a row (2) for player
    # 2: Number of pieces in a row (3) for player
    # 3: Number of center column pieces for player
    # 4: Number of pieces in a row (2) for opponent
    # 5: Number of pieces in a row (3) for opponent

    def __init__(self, epsilon: float = 1):
        self.board = [[None] * self.COLS_NUM for _ in range(self.ROWS_NUM)]
        self.epsilon = epsilon
        self.weights = np.zeros(self.FEATURE_COUNT)
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

    # ------ td learning agent with linear approximation -------
    
    def extract_features(self, player: int):
        """Extract features from the current board state for linear approximation"""
        features = np.zeros(self.FEATURE_COUNT)
        
        # Feature 0: Bias term
        features[0] = 1.0
        
        # Initialize counters for features
        player_2_in_row = 0
        player_3_in_row = 0
        opponent_2_in_row = 0
        opponent_3_in_row = 0
        player_center = 0
        
        opponent = 1 - player
        
        # Count center column pieces for player
        center_col = self.COLS_NUM // 2
        for row in range(self.ROWS_NUM):
            if self.board[row][center_col] == player:
                player_center += 1
                
        # Check horizontal, vertical, and diagonal lines
        # Horizontal
        for row in range(self.ROWS_NUM):
            for col in range(self.COLS_NUM - 1):
                # Check for player's 2 in a row
                if col <= self.COLS_NUM - 2:
                    if all(self.board[row][col + i] == player for i in range(2)):
                        player_2_in_row += 1
                # Check for player's 3 in a row
                if col <= self.COLS_NUM - 3:
                    if all(self.board[row][col + i] == player for i in range(3)):
                        player_3_in_row += 1
                # Check for opponent's 2 in a row
                if col <= self.COLS_NUM - 2:
                    if all(self.board[row][col + i] == opponent for i in range(2)):
                        opponent_2_in_row += 1
                # Check for opponent's 3 in a row
                if col <= self.COLS_NUM - 3:
                    if all(self.board[row][col + i] == opponent for i in range(3)):
                        opponent_3_in_row += 1
        
        # Vertical
        for col in range(self.COLS_NUM):
            for row in range(self.ROWS_NUM - 1):
                # Check for player's 2 in a row
                if row <= self.ROWS_NUM - 2:
                    if all(self.board[row + i][col] == player for i in range(2)):
                        player_2_in_row += 1
                # Check for player's 3 in a row
                if row <= self.ROWS_NUM - 3:
                    if all(self.board[row + i][col] == player for i in range(3)):
                        player_3_in_row += 1
                # Check for opponent's 2 in a row
                if row <= self.ROWS_NUM - 2:
                    if all(self.board[row + i][col] == opponent for i in range(2)):
                        opponent_2_in_row += 1
                # Check for opponent's 3 in a row
                if row <= self.ROWS_NUM - 3:
                    if all(self.board[row + i][col] == opponent for i in range(3)):
                        opponent_3_in_row += 1
        
        # Assign counts to features
        features[1] = player_2_in_row
        features[2] = player_3_in_row
        features[3] = player_center
        features[4] = opponent_2_in_row
        features[5] = opponent_3_in_row
        
        return features
    
    def calculate_value(self, features):
        return np.dot(self.weights, features)

    # choosing moves in agent
    def td_agent_move(self, player: int):
        # extract features for current state
        current_features = self.extract_features(player)
        
        # choose the best from valid states OR random (depending on epsilon)
        possible_moves = self.all_possible_moves()
        if random() < self.epsilon:
            chosen_col = choice(possible_moves)
        else:
            best_value = -float('inf')
            best_move = None
            for col in possible_moves:
                # simulate move
                row, _ = self.move(col, player)
                # evaluate resulting state
                next_features = self.extract_features(player)
                value = self.calculate_value(next_features)
                # undo move
                self.board[row][col] = None
                # find the best move
                if value > best_value:
                    best_value = value
                    best_move = col
            chosen_col = best_move if best_move is not None else choice(possible_moves)
        
        # actually do the chosen move
        row, col = self.move(chosen_col, player)
        
        # store state features for learning
        self.history.append(current_features)

    # when state is terminal, I need to update the weights
    def update_weights(self, reward: float):
        target = 0
        
        # Iterate through history in reverse and update weights
        for features in reversed(self.history):
            # Current estimated value
            current_value = self.calculate_value(features)
            
            # TD error: δ = r + γ*V'(s) - V(s)
            td_error = reward + target - current_value
            
            # Update weights: w = w + α·δ·f(s) (with clipping to prevent overflow)
            update = self.ALPHA * td_error * features
            # Clip update to prevent exploding values
            update = np.clip(update, -1.0, 1.0)
            self.weights += update
            
            # # Clip weights to reasonable range
            self.weights = np.clip(self.weights, 0.0, 1.0)

            # # Next target includes discounted current value
            target = self.calculate_value(features) * self.GAMMA


"""
Result: td learning agent with linear approximation
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
            game.update_weights(1.0)
            td_wins += 1
            # print(f"Player {td_player} wins")
        elif rew == random_player:
            game.update_weights(0.0)
            # print(f"Player {random_player} wins")
        else:
            game.update_weights(0.5)
            # print(f"DRAW")

        if i % 100 == 0:
            print(f"After {i} games, TD agent won {td_wins} times in last 100 games ({(td_wins / 100) * 100:.1f}%)")
            print(f"Current weights: {game.weights}")
            td_wins = 0

        game.reset_game()







