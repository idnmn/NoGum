import pygame
import config
import random
from pygame import Vector2
from typing import List
from models.enemies import Enemy
from models.game_state import GameState
from models.projectile import Projectile


class ProjectileSystem:
    def __init__(self, state: GameState) -> None:
        self._state = state
        self.projectiles: list[Projectile] = []

        self._limit = 100

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

                chest = active_room.chest
                if chest and p.rect.colliderect(chest.body.rect):
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

        while len(self.projectiles) > self._limit:
            self.projectiles.pop(0)

    def _on_wall_impact(self, pos: tuple[float, float]) -> None:
        distance = Vector2((self._state.player.rect.centerx - pos[0],
                            self._state.player.rect.centery - pos[1])).magnitude()
        ratio = (1200 - distance) * 0.0015
        if ratio <= 0:
            ratio = 0

        self._state.particle_system.spawn_wall_impact(pos, color=config.MINIMAP_WALL_COLOR_LIST[self._state.level_seed - 1])
        self._state.camera.shake(config.IMPACT_SHAKE_AMOUNT * ratio, config.IMPACT_SHAKE_DURATION)

        self._state.audio_manager.play_sound(f'wall_impact_{random.randint(1, 4)}', ratio)


    def _on_enemy_impact(self, pos: tuple[float, float], enemy) -> None:
        self._state.particle_system.spawn_enemy_impact(pos, color=enemy.impact_color)