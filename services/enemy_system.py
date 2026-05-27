import pygame
from models.enemies import Enemy
from models.game_state import GameState


class EnemySystem:
    def __init__(self) -> None:
        self.enemies: list[Enemy] = []

    def update(self, dt: float, state: GameState, surface: pygame.Surface) -> None:
        dead = []

        # отчищаем дебаг рендер
        surface.fill((0, 0, 0, 0))

        for enemy in self.enemies:
            if not enemy.is_alive:
                dead.append(enemy)
                continue

            enemy.update(dt, surface)

        # очистка мертвяков
        for e in dead:
            e.on_death()
            self.enemies.remove(e)
