from collections import defaultdict
from random import random, choice
from typing import override

import numpy as np

from qlearning_bosses.agents.Agent import Agent
from qlearning_bosses.Bullet import Bullet


"""
Agent with extra constraint - can only shoot to adjacent angles in set.
Because of this, the agent needs to decide based on the next action = full Q learning evaluation, not the
simplified one like in previous agents.
"""
class ConstrainedAngleAgent(Agent):
    N_ACTIONS = 7  # slightly smaller set of angles, to reduce sample space
    ANGLES = np.linspace(-60, 60, N_ACTIONS)
    BIN_SIZE = 40 # slightly bigger bin
    EPSILON_MIN = 0.02
    EPSILON_DECAY = 0.9999

    def __init__(self, world, alpha=0.1, gamma=0.99, epsilon=1):
        super().__init__(world)
        self.q = defaultdict(lambda: np.zeros(self.N_ACTIONS))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.last_action_index = self.N_ACTIONS // 2

    @override
    def update_knowledge(self, prev_state, action, distance, next_state):
        discrete_next_state = (
            self._discretize_state(next_state[0], self.BIN_SIZE),
            next_state[1],
            self.last_action_index
        )
        reward = 1 / (1 + distance ** 2)
        self.epsilon = max(self.EPSILON_MIN, self.epsilon * self.EPSILON_DECAY)
        best_next_q = np.max(self.q[discrete_next_state])
        self.q[prev_state][action] += self.alpha * (reward + self.gamma * best_next_q - self.q[prev_state][action])

    @override
    @override
    def create_bullet(self, target_x: float, target_dir: float) -> Bullet:
        current_discrete_state = (
            self._discretize_state(target_x, self.BIN_SIZE),
            target_dir,
            self.last_action_index
        )

        min_index = max(0, self.last_action_index - 1)
        max_index = min(self.N_ACTIONS - 1, self.last_action_index + 1)
        valid_actions = list(range(min_index, max_index + 1))

        if random() < self.epsilon:
            action_index = choice(valid_actions)
        else:
            q_values = self.q[current_discrete_state]
            best_action = max(valid_actions, key=lambda i: q_values[i])
            action_index = best_action

        self.last_action_index = action_index
        angle = self.ANGLES[action_index]
        bullet = Bullet(world=self.world, angle_deg=angle, state=current_discrete_state, action=action_index)
        return bullet




