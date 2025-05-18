from abc import ABC, abstractmethod

import numpy as np

from mini_project.constants import SCREEN_HEIGHT_METERS, PPM, SCREEN_WIDTH
from mini_project.Bullet import Bullet


class Agent(ABC):
    N_ACTIONS = 11
    ANGLES = np.linspace(-60, 60, N_ACTIONS)
    POS_X = 5
    POS_Y = SCREEN_HEIGHT_METERS//2
    BULLET_SPEED = 50

    def __init__(self, world):
        self.world = world

    @staticmethod
    def _discretize_state(target_x: float, bin_size=25) -> int:
        """Discretize the x-position of the target into bins of N pixels."""
        x_px = target_x * PPM
        max_x = SCREEN_WIDTH
        return int(min(x_px, max_x - 1) // bin_size)

    @abstractmethod
    def create_bullet(self, state = None) -> Bullet:
        pass