from typing import override

from Box2D import b2Vec2
from qlearning_bosses.common.constants import PPM, SCREEN_WIDTH
from qlearning_bosses.targets.Target import Target


class MovingTarget(Target):

    @override
    def update(self, *args):
        x_px = self.body.position.x * PPM
        if x_px <= 150 or x_px + self.width >= SCREEN_WIDTH:
            self.direction *= -1

        self.body.linearVelocity = b2Vec2(self.direction * self.speed, 0)
