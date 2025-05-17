import pygame
import time
from Box2D import b2World
from Bullet import Bullet
from constants import SCREEN_HEIGHT, PPM, SCREEN_WIDTH, TARGET_FPS, TIME_STEP, GRAVITY
from Agent import Agent
from MovingTarget import MovingTarget

# --- Setup
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
world = b2World(gravity=(0, GRAVITY), doSleep=True)

agent = Agent(world)
target = MovingTarget(world, SCREEN_WIDTH, SCREEN_HEIGHT)
bullets: list[Bullet] = []

# --- Czas ostatniego strzału
last_shot_time = 0
SHOT_INTERVAL = 0.5  # sekundy

# --- Main loop
running = True
while running:
    screen.fill((0, 0, 0))
    target.update()

    current_time = time.time()
    if current_time - last_shot_time >= SHOT_INTERVAL:
        bullet = agent.create_bullet()
        bullets.append(bullet)
        last_shot_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    world.Step(TIME_STEP, 6, 2)

    # --- Draw
    target.draw(screen)

    for bullet in bullets:
        bullet.draw(screen)

    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()
