import random

import pygame
import math

from pygame import Vector2

import config
from models.collidable import CollisionBody
from models.room import Room
from models.game_state import GameState
from models.renderable import Renderable
from services.pathfinder import Pathfinder


class Enemy(Renderable):
    def __init__(self, x: float, y: float, size: int, enemy_type: str = "") -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x - size / 2, y - size / 2, size, size),
            layer="dynamic",
            tags={"enemy", enemy_type}
        )

        self.attack_hitbox = pygame.Rect(
                self.body.rect.x - 1,
                self.body.rect.y - 1,
                self.body.rect.width + 2,
                self.body.rect.height + 2
            )

        self.type = enemy_type
        self.hp = 0.0
        self.max_speed = 0.0
        self.attack_damage = 0.0
        self.attack_range = 0.0
        self._state_timer = 0.0
        self.state: str = ''
        self.is_alive = True
        self.impact_color = (255, 255, 255)

        self.pathfinder = Pathfinder()
        self._repath_cooldown = 0.0
        self._repath_timer = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def update(self, dt: float, state: GameState, active_room: Room, surface: pygame.Surface) -> None:
        pass

    def update_timers(self, dt: float, surface: pygame.surface, active_room: Room, state: GameState) -> None:
        if self._repath_timer > 0:
            self._repath_timer -= dt

        if self._state_timer > 0:
            self._state_timer -= dt

        if self._repath_timer <= 0 and self.state == 'chase':
            self._repath_timer = self._repath_cooldown
            self.pathfinder.search_path(Vector2(self.rect.center), Vector2(state.player.rect.center), active_room)
            if self.pathfinder.path_points:
                self.next_point = self.pathfinder.path_points[0]

            # debug рендер
            for i, point in enumerate(self.pathfinder.path_points):
                draw_point = point - active_room.offset
                pygame.draw.circle(surface, (255, 210, 80), (draw_point.x, draw_point.y), 5)

                if i == 0:
                    pygame.draw.circle(surface, (255, 210, 80), self.rect.center - active_room.offset, 5)
                    pygame.draw.line(surface, (255, 210, 80), (draw_point.x, draw_point.y),
                                     self.rect.center - active_room.offset, 3)

                if i + 1 < len(self.pathfinder.path_points):
                    next_draw = self.pathfinder.path_points[i + 1] - active_room.offset
                    pygame.draw.line(surface, (255, 210, 80), (draw_point.x, draw_point.y),
                                     (next_draw.x, next_draw.y), 3)

    def take_damage(self, amount: float) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 255, 255), self.body.rect)

class BookWorm(Enemy):
    def __init__(self, x: float, y: float, size: int, enemy_type: str = "bookworm") -> None:
        super().__init__(x, y, size, enemy_type)

        # определяем статы
        self.hp = 50
        self.max_hp = 50
        self.max_speed = 600
        self.dash_speed = 2000
        self.attack_damage = 10
        self.contact_damage = 5
        self.attack_range = 200
        self.aggr_range = 1000
        self.impact_color = (255, 50, 50)

        self.state: str = 'chase'  # chase, charge, dash, recover
        self.dash_dir = Vector2(0)
        self.pre_attack_cooldown = 0.5  # кд перед рывком
        self.post_attack_cooldown = 0.2  # кд после рывка
        self.between_dash_cooldown = 2.0 # кд между рывками
        self.dash_duration = 0.2         # длительность рывка

    def render(self, surface: pygame.Surface) -> None:
        # цветовая индикация состояния
        if self.state == "chase":
            color = (255, 255, 255)
        elif self.state == "windup":
            color = (255, 180, 50)  # Подготовка
        elif self.state == "dash":
            color = (255, 50, 50)  # Рывок
        else:
            color = (150, 150, 150)  # Восстановление
        pygame.draw.rect(surface, color, self.body.rect)

    def update(self, dt: float, state: GameState, active_room: Room, surface: pygame.Surface) -> None:
        # обновляем таймеры
        self.update_timers(dt, surface, active_room, state)

        # если ещё остались точки
        if self.pathfinder.path_points:
            distance = Vector2(self.body.rect.center).distance_to(Vector2(self.next_point))
            if distance <= config.TILE_SIZE - 5 and len(self.pathfinder.path_points) > 1:
                self.next_point = Vector2(self.pathfinder.path_points.pop(0))
                pygame.draw.circle(surface, (32, 255, 28), self.next_point - active_room.offset, 7)
        else:
            self.next_point = Vector2(self.body.rect.center)

        # Вектор и дистанция до игрока
        dist_to_player = Vector2(self.rect.center).distance_to(state.player.rect.center)
        dir_to_player = (pygame.Vector2(state.player.rect.center) - pygame.Vector2(self.rect.center)).normalize()

        # Обрабатываем логику по состояниям
        if self.state == 'chase':  # поиск игрока
            dx = self.next_point.x - self.body.rect.centerx
            dy = self.next_point.y - self.body.rect.centery

            # если игрок в радиусе атаки начинаем заряжать рывок
            if dist_to_player < self.attack_range and self._state_timer <= 0:
                self.state = "charge"
                self._state_timer = self.pre_attack_cooldown
                self.body.vx = 0.0
                self.body.vy = 0.0
                self.dash_dir = dir_to_player.copy()
            else:
                direction = Vector2(dx, dy)

                if direction.magnitude() < self.aggr_range and direction.magnitude() != 0:
                    direction = direction.normalize()
                    dx, dy = direction
                else:
                    direction = Vector2(0)
                    dx, dy = direction

                # вычисляем ускорение из pathfinder'а
                if dx != 0.0 or dy != 0.0:
                    ax = dx * self.acceleration
                    ay = dy * self.acceleration
                else:
                    ax = ay = 0.0
                    # применяем трение
                    damping = math.exp(-self.friction * dt)
                    self.body.vx *= damping
                    self.body.vy *= damping

                # интегрируем ускорение в скорость
                self.body.vx += ax * dt
                self.body.vy += ay * dt

                # ограничиваем максимальную скорость
                current_speed = self.body.velocity.magnitude()
                if current_speed > self.max_speed:
                    scale = self.max_speed / current_speed
                    self.body.vx *= scale
                    self.body.vy *= scale

                # защита от дрейфа
                if current_speed < 2.0:
                    self.body.vx = 0.0
                    self.body.vy = 0.0

        elif self.state == 'charge':  # готовится к рывку
            self.body.vx = 0.0
            self.body.vy = 0.0
            self.dash_dir = dir_to_player.copy()
            # делаем рывок
            if self._state_timer <= 0:
                self.state = "dash"
                self._state_timer = self.dash_duration
                self.body.vx = self.dash_dir.x * self.dash_speed
                self.body.vy = self.dash_dir.y * self.dash_speed

        elif self.state == "dash":
            # сбрасываем рывок при контакте или по истечению таймера
            if self.attack_hitbox.colliderect(state.player.rect) or self._state_timer <= 0:
                self.state = "recovery"
                self._state_timer = self.post_attack_cooldown
                self.body.vx = 0.0
                self.body.vy = 0.0

        elif self.state == "recovery":
            if self._state_timer <= 0:
                self.state = "chase"
                self._state_timer = self.between_dash_cooldown

        # наносим урон при столкновении
        if self.attack_hitbox.colliderect(state.player.rect):
            damage = self.contact_damage if self.state != 'dash' else self.attack_damage
            state.player.take_damage(damage)

        # обновляем позицию
        self.body.rect.x += self.body.vx * dt
        self.body.rect.y += self.body.vy * dt

        self.attack_hitbox.x = self.body.rect.x - 1
        self.attack_hitbox.y = self.body.rect.y - 1

    def _attack(self):
        pass
