from typing import override

from Box2D import b2Vec2

from qlearning_bosses.common.Bullet import Bullet
from qlearning_bosses.common.Collidable import Collidable
from qlearning_bosses.common.constants import PPM, SCREEN_WIDTH
from qlearning_bosses.targets.Target import Target


class NaiveMovingTarget(Target):

    def get_closest_bullet(self, bullets: list[Bullet]) -> Bullet | None:
        x_target, y_target, _, _ = self.get_position()

        valid_bullets = [
            b for b in bullets
            if b.get_position()[1] < y_target - self.height * 2
        ]

        if not valid_bullets:
            return None

        min(valid_bullets, key=lambda b: Collidable.distance(b, self))
        for bull in bullets:
            bull.color = (255, 0, 0)
        valid_bullets[0].color = (0, 0, 255)
        return valid_bullets[0]

    @override
    def update(self, bullets: list[Bullet]) -> None:
        start = self.body.position.x * PPM
        end = start + self.width
        if start <= 150 or end  >= SCREEN_WIDTH:
            self.direction *= -1
            self.body.linearVelocity = b2Vec2(self.direction * self.speed, 0)
            return

        b = self.get_closest_bullet(bullets)
        if b is not None:
            x_bullet, y_bullet, w_bullet, _ = b.get_position()
            if x_bullet + w_bullet < start:  # if bullet from left, move right
                self.direction = 1
            elif x_bullet < end:  # if bullet above, avoid it to the left
                self.direction = -1

        self.body.linearVelocity = b2Vec2(self.direction * self.speed, 0)