from collections import defaultdict
from random import random, randint
from typing import override, Optional

import numpy as np


from qlearning_bosses.agents.Agent import Agent
from qlearning_bosses.common.Bullet import Bullet


"""
Agent with cooldown - needs 10 ticks to cooldown after shooting.
Reward depends on distance to target (similar to the other agents) but also gives small reward for waiting,
but starts to punish if waiting too long.
"""
class AgentWithCooldown(Agent):
    EPSILON_MIN = 0.001
    EPSILON_DECAY = 0.995
    COOLDOWN = 10  # time of cooldown in ticks

    def __init__(self, world, alpha=0.1, epsilon=1):
        super().__init__(world)
        self.WAIT_ACTION_INDEX = self.N_ACTIONS
        self.q = defaultdict(lambda: np.zeros(self.N_ACTIONS + 1))
        self.alpha = alpha
        self.epsilon = epsilon
        self.time_since_last_shot = 0

    @override
    def update_knowledge(self, state, action, distance, next_state = None):
        if distance == 0:  # hit
            reward = 1
        elif distance > 0:  # miss
            reward = 1 / (100 + 10 * distance**2)
        else:
            # little reward for waiting - better than missing, but punish on waiting too long!
            reward = 1 / (10 * max(self.time_since_last_shot, self.COOLDOWN))
        self.epsilon = max(self.EPSILON_MIN, self.epsilon * self.EPSILON_DECAY)
        self.q[state][action] += self.alpha * (reward - self.q[state][action])

    @override
    def create_bullet(self, target_x: float, target_dir: float) -> Optional[Bullet]:
        self.time_since_last_shot += 1
        discrete_state = self._discretize_state(target_x), target_dir

        if self.time_since_last_shot < self.COOLDOWN:
            self.update_knowledge(discrete_state, self.WAIT_ACTION_INDEX, -1)
            return None

        if random() < self.epsilon:
            action_index = randint(0, self.N_ACTIONS)
        else:
            action_index = np.argmax(self.q[discrete_state])

        if action_index == self.WAIT_ACTION_INDEX:
            self.update_knowledge(discrete_state, self.WAIT_ACTION_INDEX, -1)
            return None

        self.time_since_last_shot = 0
        angle = self.ANGLES[action_index]
        bullet = Bullet(world=self.world, angle_deg=angle, state=discrete_state, action=action_index)
        bullet.action = action_index
        return bullet


