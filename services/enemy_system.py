import pygame
import config
from models.enemies import Enemy
from models.game_state import GameState
from models.player import Player
from models.room_manager import RoomManager

class EnemySystem:
    def __init__(self) -> None:
        self.enemies: list[Enemy] = []

    def update(self, dt: float, state: GameState) -> None:
        dead = []
        for enemy in self.enemies:
            if not enemy.is_alive:
                dead.append(enemy)
                continue

            enemy.update_timers(dt)
            enemy.update(dt, state)
            # self._try_attack(enemy, state.player)

        # Очистка (DRY)
        for e in dead:
            self.enemies.remove(e)


    def _try_attack(self, enemy: Enemy, player: Player) -> None:
        dx = enemy.rect.centerx - player.rect.centerx
        dy = enemy.rect.centery - player.rect.centery
        dist = (dx*dx + dy*dy) ** 0.5

        if dist < enemy.attack_range + config.PLAYER_SIZE / 2:
            if enemy.can_attack():
                player.current_hp = max(0, player.current_hp - enemy.attack_damage)
                enemy.reset_attack_cooldown()