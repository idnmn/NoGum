import pygame
import math

from pygame import Vector2

import config
from models.collidable import CollisionBody
from models.game_state import GameState
from models.renderable import Renderable

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

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def update(self, dt: float, state: GameState) -> None:
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
        self.max_speed = 400
        self.attack_damage = 5
        self.attack_range = 50
        self.attack_cooldown = 3.0
        self.aggr_range = 1000
        self.impact_color = (255, 50, 50)

        self.acceleration = 1500
        self.friction = config.FRICTION
        self.vx = 0.0
        self.vy = 0.0

    def render(self, surface: pygame.Surface) -> None:
        # Заглушка: белый прямоугольник (потом заменим на спрайт)
        pygame.draw.rect(surface, (255, 255, 255), self.body.rect)

    def update(self, dt: float, state: GameState) -> None:
        dx = state.player.rect.centerx - self.body.rect.centerx
        dy = state.player.rect.centery - self.body.rect.centery
        direction = Vector2(dx, dy)

        if direction.magnitude() < self.aggr_range and direction.magnitude() != 0:
            direction = direction.normalize()
            dx, dy = direction
        else:
            direction = Vector2(0)


        # вычисляем ускорение из ввода
        if dx != 0.0 or dy != 0.0:
            length = math.hypot(dx, dy)
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
        current_speed = math.hypot(self.vx, self.vy)

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


