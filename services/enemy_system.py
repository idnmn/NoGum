import pygame
import config
from models.enemies import Enemy
from models.game_state import GameState
from models.player import Player
from models.room import Room

class EnemySystem:
    def __init__(self) -> None:
        self.enemies: list[Enemy] = []

    def update(self, dt: float, state: GameState, active_room: Room, surface: pygame.Surface) -> None:
        dead = []

        # отчищаем дебаг рендер
        surface.fill((0, 0, 0, 0))

        for enemy in self.enemies:
            if not enemy.is_alive:
                dead.append(enemy)
                continue

            enemy.update(dt, state, active_room, surface)

        # очистка мертвяков
        for e in dead:
            self.enemies.remove(e)
