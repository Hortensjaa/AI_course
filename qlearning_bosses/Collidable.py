from abc import ABC, abstractmethod
from typing import Tuple

import pygame


class Collidable(ABC):

    @abstractmethod
    def get_position(self)  -> Tuple[float, float, float, float]:
        """
        Returns the position of the collidable object.
        The position is represented as a tuple (x, y, width, height).
        """
        pass

    @abstractmethod
    def draw(self, screen: pygame.display) -> None:
        pass

    def are_colliding(self, other: 'Collidable') -> bool:
        """
        Checks if this collidable object is colliding with another collidable object.
        """
        x1, y1, w1, h1 = self.get_position()
        x2, y2, w2, h2 = other.get_position()

        return (x1 < x2 + w2 and
                x1 + w1 > x2 and
                y1 < y2 + h2 and
                y1 + h1 > y2)
