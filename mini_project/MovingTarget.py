from typing import override, Tuple

import pygame
from Box2D import b2World, b2Vec2
from Collidable import Collidable
from constants import PPM, SCREEN_HEIGHT

class MovingTarget(Collidable):
    def __init__(self, world: b2World, wx_px: int, wy_px: int, width_px=100, height_px=10, speed_px=500):
        self.wx = wx_px
        self.wy = wy_px
        self.width = width_px
        self.height = height_px
        self.speed = speed_px / PPM  # convert to meters per step

        # Convert pixels to meters
        init_x = (wx_px / 2) / PPM
        init_y = (SCREEN_HEIGHT - height_px) / PPM

        self.body = world.CreateKinematicBody(
            position=b2Vec2(init_x, init_y)
        )
        self.body.CreatePolygonFixture(box=(width_px / 2 / PPM, height_px / 2 / PPM))

        self.direction = 1

    def update(self):
        # Get position in pixels
        x_px = self.body.position.x * PPM
        if x_px <= 0:
            self.direction = 1
        elif x_px + self.width >= self.wx:
            self.direction = -1

        self.body.linearVelocity = b2Vec2(self.direction * self.speed, 0)

    @override
    def get_position(self) -> Tuple[int, int, int, int]:
        pos = self.body.position
        x_px = int(pos.x * PPM)
        y_px = int(pos.y * PPM)
        return x_px, y_px, self.width, self.height

    def draw(self, screen: pygame.display) -> None:
        x, y, w, h = self.get_position()
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(x, y, w, h))