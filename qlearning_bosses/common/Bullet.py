import math
import pygame
from Box2D import b2World, b2Vec2
from typing import override, Tuple

from qlearning_bosses.common.Collidable import Collidable
from qlearning_bosses.common.constants import PPM, SCREEN_HEIGHT, SCREEN_HEIGHT_METERS


class Bullet(Collidable):
    def __init__(self, world: b2World, x = 5, y= SCREEN_HEIGHT_METERS//2, angle_deg = 0, speed = 50,
                 state = None, action = None):
        self.body = world.CreateDynamicBody(position=(x, y), bullet=True)
        self.body.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=100)
        self.color = (255, 0, 0)

        angle_rad = math.radians(angle_deg)
        vx = speed * math.cos(angle_rad)
        vy = speed * math.sin(angle_rad)
        self.body.linearVelocity = b2Vec2(vx, vy)

        self.width = 1
        self.height = 1

        self.state = state
        self.action = action

    @override
    def get_position(self) -> Tuple[float, float, float, float]:
        x, y = self.body.position
        px = x * PPM
        py = SCREEN_HEIGHT - y * PPM
        return px, py, self.width * PPM, self.height * PPM

    @override
    def draw(self, screen: pygame.display) -> None:
        x, y, w, h = self.get_position()
        pygame.draw.rect(screen, self.color, pygame.Rect(x, y, w, h))
