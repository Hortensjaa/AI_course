from abc import ABC, abstractmethod

import numpy as np

from constants import SCREEN_HEIGHT_METERS
from Bullet import Bullet


class Agent(ABC):
    N_ACTIONS = 5
    ANGLES = np.linspace(-60, 85, N_ACTIONS)
    POS_X = 5
    POS_Y = SCREEN_HEIGHT_METERS//2
    BULLET_SPEED = 50

    def __init__(self, world):
        self.world = world

    @abstractmethod
    def create_bullet(self, state = None) -> Bullet:
        pass