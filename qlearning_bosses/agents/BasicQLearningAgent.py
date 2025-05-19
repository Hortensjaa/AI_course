from collections import defaultdict
from random import random, randint
from typing import override

import numpy as np

from qlearning_bosses.agents.Agent import Agent
from qlearning_bosses.common.Bullet import Bullet


"""
Basic QLearning agent trying to aim to the target.
It uses a simplified Q-learning algorithm to learn the best action to take in each state (discrete target position and direction).
Gets a reward based on the distance to the target, with big advantage for hit.
"""
class BasicQLearningAgent(Agent):
    EPSILON_MIN = 0.01
    EPSILON_DECAY = 0.999

    def __init__(self, world, alpha=0.1, epsilon=1):
        super().__init__(world)
        self.q = defaultdict(lambda: np.zeros(self.N_ACTIONS))
        self.alpha = alpha
        self.epsilon = epsilon

    @override
    def update_knowledge(self, state, action, distance, next_state = None):
        if distance > 0:
            reward = 1 / (10 + distance**2)
        else:
            reward = 1
        self.epsilon = max(self.EPSILON_MIN, self.epsilon * self.EPSILON_DECAY)
        self.q[state][action] += self.alpha * (reward - self.q[state][action])

    @override
    def create_bullet(self, target_x: float, target_dir: float) -> Bullet:
        discrete_state = self._discretize_state(target_x), target_dir
        if random() < self.epsilon:
            action_index = randint(0, self.N_ACTIONS - 1)
        else:
            action_index = np.argmax(self.q[discrete_state])

        angle = self.ANGLES[action_index]
        bullet = Bullet(world=self.world, angle_deg=angle, state=discrete_state, action=action_index)
        bullet.action = action_index
        return bullet


