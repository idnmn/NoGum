import math
import pygame
import config
from models.collidable import CollisionBody

class Player:
    def __init__(self, x: float, y: float) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, config.PLAYER_SIZE, config.PLAYER_SIZE),
            layer="dynamic",
            tags={"player"}
        )
        self.vx = 0.0
        self.vy = 0.0

        # состояние рывка (таймеры)
        self._dash_timer: float = 0.0
        self._dash_cooldown_timer: float = 0.0

        # подтягиваем статы из конфига
        self.max_speed = config.PLAYER_MAX_SPEED
        self.acceleration = config.PLAYER_ACCELERATION
        self.friction = config.PLAYER_FRICTION
        self.dash_speed = config.PLAYER_DASH_SPEED
        self.dash_cooldown = config.PLAYER_DASH_COOLDOWN
        self.dash_duration = config.PLAYER_DASH_DURATION

    def update(self, dx: float, dy: float, dt: float, dash_requested: bool) -> None:
        """
        dx, dy: Направление ввода
        dt: Delta time в секундах
        dash_requested - флаг отработки рывка
        """

        # обновляем таймер для кд
        if self._dash_cooldown_timer > 0:
            self._dash_cooldown_timer -= dt

        # делаем рывок (коли можем)
        if dash_requested and self._dash_cooldown_timer <= 0 and (dx != 0 or dy != 0):
            self._dash_timer = self.dash_duration
            self._dash_cooldown_timer = self.dash_cooldown
        # обновляем таймер для рывка
        if self._dash_timer > 0:
            self._dash_timer -= dt

        # используем параметры рывка, пока активен его таймер
        current_max_speed = self.dash_speed if self._dash_timer > 0 else self.max_speed
        current_accel = self.acceleration * 10 if self._dash_timer > 0 else self.acceleration

        # вычисляем ускорение из ввода
        if dx != 0.0 or dy != 0.0:
            length = math.hypot(dx, dy)
            ax = (dx / length) * current_accel
            ay = (dy / length) * current_accel
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
            scale = current_max_speed / current_speed
            self.vx *= scale
            self.vy *= scale

        # защита от дрейфа
        if current_speed < 2.0:
            self.vx = 0.0
            self.vy = 0.0

        # обновляем позицию и обрабатываем коллизии
        self.body.rect.x += self.vx * dt
        self.body.rect.y += self.vy * dt
