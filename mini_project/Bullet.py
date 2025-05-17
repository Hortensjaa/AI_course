import math
import pygame
from Box2D import b2World, b2Vec2
from typing import override, Tuple

from Collidable import Collidable
from constants import PPM, SCREEN_HEIGHT


class Bullet(Collidable):
    def __init__(self, world: b2World, x: int, y: int, angle_deg: int, speed: int):
        self.body = world.CreateDynamicBody(position=(x, y), bullet=True)
        self.body.CreatePolygonFixture(box=(0.1, 0.1), density=1, friction=100)

        angle_rad = math.radians(angle_deg)
        vx = speed * math.cos(angle_rad)
        vy = speed * math.sin(angle_rad)
        self.body.linearVelocity = b2Vec2(vx, vy)

        self.width = 1
        self.height = 1

    @override
    def get_position(self) -> Tuple[int, int, int, int]:
        x, y = self.body.position
        px = int(x * PPM)
        py = SCREEN_HEIGHT - int(y * PPM)
        return px, py, int(self.width * PPM), int(self.height * PPM)

    @override
    def draw(self, screen: pygame.display) -> None:
        x, y, w, h = self.get_position()
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(x, y, w, h))
