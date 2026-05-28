import pygame
from typing import Callable, List
from models.enemies import Enemy
from models.game_state import GameState
from models.projectile import Projectile


class ProjectileSystem:
    def __init__(self, on_wall_impact: Callable[[tuple[float, float]], None],
                 on_enemy_impact: Callable[[tuple[float, float]], None], state: GameState) -> None:
        self._state = state
        self.projectiles: list[Projectile] = []
        self._on_wall_impact = on_wall_impact
        self._on_enemy_impact = on_enemy_impact

    def spawn(self, projectile, origin: pygame.Vector2, direction: pygame.Vector2) -> None:
        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)

        weapon = self._state.weapon

        size = weapon.get_size()
        speed = weapon.get_speed()

        vel = direction.normalize() * speed

        self.projectiles.append(projectile(x=origin.x, y=origin.y, size=size,
                                           velocity=vel, damage=weapon.damage, lifetime=10.0))

    def update(self, dt: float, enemies: List[Enemy]) -> None:
        for p in self.projectiles:
            p.rect.x += p.velocity.x * dt
            p.rect.y += p.velocity.y * dt
            p.lifetime -= dt

            if p.lifetime <= 0:
                p.is_active = False
                continue

            # коллизия со стенами только активной комнаты
            active_room = self._state.room_manager.active_room
            if active_room:
                for wall in active_room.walls:
                    if p.rect.colliderect(wall.body.rect):
                        p.is_active = False
                        self._on_wall_impact((p.rect.centerx, p.rect.centery))
                        break
                terminal = active_room.terminal
                if terminal and p.rect.colliderect(terminal.body.rect):
                    p.is_active = False
                    self._on_wall_impact((p.rect.centerx, p.rect.centery))
                    break

            # коллизия с врагами
            for enemy in enemies:
                if p.rect.colliderect(enemy.body.rect):
                    p.is_active = False
                    if enemy.take_damage(p.damage):
                        self._state.stattracker.damage_dealt += int(p.damage)
                        self._on_enemy_impact((p.rect.centerx, p.rect.centery), enemy)

        # очистка неактивных снарядов
        self.projectiles = [p for p in self.projectiles if p.is_active]