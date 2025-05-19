from Box2D import b2Vec2
from qlearning_bosses.common.constants import PPM
from qlearning_bosses.targets.Target import Target


class MovingTarget(Target):

    def update(self):
        x_px = self.body.position.x * PPM
        if x_px <= 150 or x_px + self.width >= self.wx:
            self.direction *= -1

        self.body.linearVelocity = b2Vec2(self.direction * self.speed, 0)
