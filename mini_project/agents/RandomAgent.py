from random import choice
from typing import override

from mini_project.Bullet import Bullet
from mini_project.agents.Agent import Agent


class RandomAgent(Agent):

    def __init__(self, world):
        super().__init__(world)

    @override
    def create_bullet(self, state = None) -> Bullet:
        deg = choice(self.ANGLES)
        return Bullet(self.world, x=self.POS_X, y=self.POS_Y, angle_deg=int(deg))