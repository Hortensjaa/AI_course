from random import choice
from typing import override

from qlearning_bosses.common.Bullet import Bullet
from qlearning_bosses.agents.Agent import Agent


class RandomAgent(Agent):

    def __init__(self, world):
        super().__init__(world)

    @override
    def update_knowledge(self, state = None, action = None, distance = None, next_state = None):
        pass

    @override
    def create_bullet(self, target_x: float = None, target_dir: float = None) -> Bullet:
        deg = choice(self.ANGLES)
        return Bullet(self.world, x=self.POS_X, y=self.POS_Y, angle_deg=int(deg))