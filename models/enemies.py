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
        self.type = enemy_type
        self.hp = 0.0
        self.max_speed = 0.0
        self.attack_damage = 0.0
        self.attack_range = 0.0
        self.attack_cooldown = 0.0
        self._attack_timer = 0.0
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

    def can_attack(self) -> bool:
        return self._attack_timer <= 0

    def reset_attack_cooldown(self) -> None:
        self._attack_timer = self.attack_cooldown

    def update_timers(self, dt: float) -> None:
        if self._attack_timer > 0:
            self._attack_timer -= dt

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
        self.attack_damage = 5
        self.attack_range = 50
        self.attack_cooldown = 3.0
        self.aggr_range = 1000
        self.impact_color = (255, 50, 50)

        self.acceleration = 2500
        self.friction = config.FRICTION * 10
        self.vx = 0.0
        self.vy = 0.0
        self.next_point = Vector2(self.rect.center)

        self._repath_cooldown = 0.3

    def render(self, surface: pygame.Surface) -> None:
        # Заглушка: белый прямоугольник (потом заменим на спрайт)
        pygame.draw.rect(surface, (255, 255, 255), self.body.rect)

    def update(self, dt: float, state: GameState, active_room: Room, surface: pygame.Surface) -> None:
        if self._repath_timer > 0:
            self._repath_timer -= dt

        if self._repath_timer <= 0:
            self._repath_timer = self._repath_cooldown
            self.pathfinder.search_path(Vector2(self.rect.center), Vector2(state.player.rect.center), active_room)
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


        # если ещё остались точки
        if self.pathfinder.path_points:
            # print('POINTS:', len(self.pathfinder.path_points))
            # print('DIST:', Vector2(self.body.rect.center).distance_to(Vector2(self.next_point)))
            distance = Vector2(self.body.rect.center).distance_to(Vector2(self.next_point))
            if distance <= config.TILE_SIZE - 5 and len(self.pathfinder.path_points) > 1:
                # print('SWITCH POINT')
                self.next_point = Vector2(self.pathfinder.path_points.pop(0))
                pygame.draw.circle(surface, (32, 255, 28), self.next_point - active_room.offset, 7)
        else:
            # print('STAY')
            self.next_point = Vector2(self.body.rect.center)


        dx = (self.next_point.x) - self.body.rect.centerx
        dy = (self.next_point.y) - self.body.rect.centery
        direction = Vector2(dx, dy)

        if direction.magnitude() < self.aggr_range and direction.magnitude() != 0:
            direction = direction.normalize()
            dx, dy = direction
        else:
            direction = Vector2(0)
            dx, dy = direction


        # вычисляем ускорение из ввода
        if dx != 0.0 or dy != 0.0:
            ax = dx * self.acceleration
            ay = dy * self.acceleration
        else:
            ax = ay = 0.0
            # применяем трение
            damping = math.exp(-self.friction * dt)
            self.vx *= damping
            self.vy *= damping

        # интегрируем ускорение в скорость
        self.vx += ax * dt
        self.vy += ay * dt

        # ограничиваем максимальную скорость
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed > self.max_speed:
            scale = self.max_speed / current_speed
            self.vx *= scale
            self.vy *= scale

        # защита от дрейфа
        if current_speed < 2.0:
            self.vx = 0.0
            self.vy = 0.0

        # обновляем позицию
        self.body.rect.x += self.vx * dt
        self.body.rect.y += self.vy * dt
