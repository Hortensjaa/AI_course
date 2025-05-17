from collections import defaultdict
from random import random, randint
from typing import override

import numpy as np


from mini_project.Agent import Agent
from mini_project.Bullet import Bullet
from constants import SCREEN_WIDTH, PPM


class BasicQLearningAgent(Agent):
    EPSILON_MIN = 0.01
    EPSILON_DECAY = 0.999

    def __init__(self, world, alpha=0.2, gamma=0.99, epsilon=1):
        super().__init__(world)
        self.q = defaultdict(lambda: np.zeros(self.N_ACTIONS))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def _discretize_state(self, target_x: float) -> int:
        """Discretize the x-position of the target into bins of N pixels."""
        x_px = target_x * PPM
        bin_size = 50
        max_x = SCREEN_WIDTH
        return int(min(x_px, max_x - 1) // bin_size)

    def update_knowledge(self, state, action, distance):
        reward = 1 / (1 + distance**2)
        self.epsilon = max(self.EPSILON_MIN, self.epsilon * self.EPSILON_DECAY)
        self.q[state][action] += reward
        self.q[state][action] += self.alpha * (reward - self.q[state][action])

    @override
    def create_bullet(self, state) -> Bullet:
        discrete_state = self._discretize_state(state[0]), state[1]
        if random() < self.epsilon:
            action_index = randint(0, self.N_ACTIONS - 1)
        else:
            action_index = np.argmax(self.q[discrete_state])

        angle = self.ANGLES[action_index]
        bullet = Bullet(world=self.world, angle_deg=angle, state=discrete_state, action=action_index)
        bullet.action = action_index
        return bullet


