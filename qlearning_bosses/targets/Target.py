from typing import override, Tuple

import pygame
from Box2D import b2World, b2Vec2

from qlearning_bosses.common.Collidable import Collidable
from qlearning_bosses.common.constants import PPM, SCREEN_HEIGHT, SCREEN_WIDTH

class Target(Collidable):
    def __init__(self, world: b2World, width_px=100, height_px=10, speed_px=500):
        self.width = width_px
        self.height = height_px
        self.speed = speed_px / PPM

        init_x = (SCREEN_WIDTH / 2) / PPM
        init_y = (SCREEN_HEIGHT - height_px) / PPM

        self.body = world.CreateKinematicBody(
            position=b2Vec2(init_x, init_y)
        )
        self.body.CreatePolygonFixture(box=(width_px / 2 / PPM, height_px / 2 / PPM))

        self.direction = 1

    def update(self, *args):
        pass

    @override
    def get_position(self) -> Tuple[float, float, float, float]:
        pos = self.body.position
        x_px = pos.x * PPM
        y_px = pos.y * PPM
        return x_px, y_px, self.width, self.height

    def draw(self, screen: pygame.display) -> None:
        x, y, w, h = self.get_position()
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(x, y, w, h))