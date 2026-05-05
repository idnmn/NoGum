import random
import pygame
import config
from models.enemies import *


class Spawner:
    def spawn_bookworm(self, x: float, y: float) -> Enemy:
        return BookWorm(x, y, size=32, enemy_type='bookworm')

    # def spawn_in_area(self, area: pygame.Rect, count: int, enemy: Enemy) -> list[Enemy]:
    #     margin = 20
    #     enemies = []
    #     for _ in range(count):
    #         if area.width < config.ENEMY_SIZE or area.height < config.ENEMY_SIZE:
    #             continue
    #         x = random.uniform(area.x + margin, area.right - config.ENEMY_SIZE - margin)
    #         y = random.uniform(area.y + margin, area.bottom - config.ENEMY_SIZE - margin)
    #         enemies.append(self.spawn(x, y, enemy_type))
    #     return enemies
