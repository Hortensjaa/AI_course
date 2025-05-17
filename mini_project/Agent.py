from collections import defaultdict
from random import random, randint, choice

import numpy as np

from Bullet import Bullet
from constants import SCREEN_HEIGHT_METERS


class Agent:
    N_ACTIONS = 10
    ANGLES = np.linspace(-60, 85, N_ACTIONS)

    def __init__(self, world, alpha=0.1, gamma=0.99, epsilon=0.1):
        self.q = defaultdict(lambda: np.zeros(self.N_ACTIONS))
        self.world = world
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def select_action(self, state):
        if random() < self.epsilon:
            return randint(0, self.N_ACTIONS - 1)
        return np.argmax(self.q[state])

    def update(self, state, action, reward, next_state, done):
        best_next = np.max(self.q[next_state])
        target = reward if done else reward + self.gamma * best_next
        self.q[state][action] += self.alpha * (target - self.q[state][action])

    def create_bullet(self) -> Bullet:
        # -- for tests
        deg = choice(self.ANGLES)
        return Bullet(self.world, x=5, y=SCREEN_HEIGHT_METERS//2, angle_deg=int(deg), speed=50)
        # ------------
