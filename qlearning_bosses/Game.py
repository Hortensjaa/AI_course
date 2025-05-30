from time import time

import pygame
from Box2D import b2World

from qlearning_bosses.common.Bullet import Bullet
from qlearning_bosses.common.Timer import Timer
from qlearning_bosses.common.constants import GRAVITY, SCREEN_HEIGHT, SCREEN_WIDTH, TARGET_FPS, TIME_STEP

class Game:
    COUNTER_RESET_INTERVAL = 10

    def __init__(self, agent_cls, target_cls, cooldown = 0.01):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.shot_cooldown = cooldown

        self.world = b2World(gravity=(0, GRAVITY), doSleep=True)
        self.agent = agent_cls(self.world)
        self.target = target_cls(self.world)
        self.bullets: list[Bullet] = []

        self.history = []
        self.shot_timer = Timer(self.shot_cooldown)
        self.reset_timer = Timer(self.COUNTER_RESET_INTERVAL)

        self.success_counter = 0
        self.miss_counter = 0

        self.button_rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 110, 40)

    def run(self, sim_time: int = 100):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(TARGET_FPS)
            if len(self.history) == sim_time:
                break
        self._print_history()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_rect.collidepoint(event.pos):
                    self._print_history()

    def _update(self):
        self.screen.fill((0, 0, 0))
        self.target.update(self.bullets)

        if self.shot_timer.ready():
            bullet = self.agent.create_bullet(self.target.body.position.x, self.target.direction)
            if bullet is not None:
                self.bullets.append(bullet)
            self.shot_timer.reset()

        self.world.Step(TIME_STEP, 6, 2)

        for bullet in self.bullets[:]:
            bullet.draw(self.screen)
            bullet_x, bullet_y = bullet.body.position
            target_x, _ = self.target.body.position

            if self.target.are_colliding(bullet):
                self._destroy_bullet(bullet)
                self.success_counter += 1
                self.agent.update_knowledge(bullet.state, bullet.action, 0, (target_x, self.target.direction))
            elif bullet_y < 0:
                self._destroy_bullet(bullet)
                self.miss_counter += 1
                self.agent.update_knowledge(bullet.state, bullet.action, abs(target_x - bullet_x),
                                            (target_x, self.target.direction))

        if self.reset_timer.ready():
            self.history.append((self.success_counter, self.miss_counter))
            self.success_counter = 0
            self.miss_counter = 0
            self.reset_timer.reset()

    def _destroy_bullet(self, bullet: Bullet):
        self.world.DestroyBody(bullet.body)
        self.bullets.remove(bullet)

    def _draw(self):
        self.target.draw(self.screen)
        self._draw_counters()
        self._draw_reset_timer()
        self._draw_history_button()
        pygame.display.flip()

    def _draw_counters(self):
        total = self.success_counter + self.miss_counter
        success_rate = (self.success_counter / total * 100) if total > 0 else 0
        counter_text = (
            f"Hits: {self.success_counter}  "
            f"Misses: {self.miss_counter}  "
            f"Success rate: {success_rate:.1f}%"
        )
        font = pygame.font.SysFont("Arial", 24)
        text_surface = font.render(counter_text, True, (255, 255, 255))
        self.screen.blit(text_surface, (10, 10))

    def _draw_reset_timer(self):
        time_left = max(0, self.COUNTER_RESET_INTERVAL - (time() - self.reset_timer.last_time))
        timer_text = f"Reset in: {int(time_left)}s"
        font = pygame.font.SysFont("Arial", 18)
        text_surface = font.render(timer_text, True, (200, 200, 0))
        self.screen.blit(text_surface, (10, 40))

    def _draw_history_button(self):
        pygame.draw.rect(self.screen, (70, 70, 200), self.button_rect)
        font = pygame.font.SysFont("Arial", 16)
        label = font.render("Print history", True, (255, 255, 255))
        label_rect = label.get_rect(center=self.button_rect.center)
        self.screen.blit(label, label_rect)

    def _print_history(self):
        print("=== History ===")
        all_hits = 0
        all_misses = 0
        for i, (hits, misses) in enumerate(self.history):
            if 1 % 100 == 0:
                print("-------------------")
            all_hits += hits
            all_misses += misses
            total = hits + misses
            success_rate = (hits / total * 100) if total > 0 else 0
            print(f"{i + 1}. Hits: {hits}, Misses: {misses}, Success rate: {success_rate:.1f}% {"<- PASSED" if success_rate > 90 else ""}")
        print("-----Total-----")
        total = all_hits + all_misses
        success_rate = (all_hits / total * 100) if total > 0 else 0
        print(f"Hits: {all_hits}, Misses: {all_misses}, Success rate: {success_rate:.1f}%")
        print("===============")
        print()
