import math
import pygame
import config
from models.collidable import CollisionBody
from models.renderable import Renderable


class Player(Renderable):
    def __init__(self, x: float, y: float, sprite: pygame.Surface) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, config.PLAYER_SIZE, config.PLAYER_SIZE),
            layer="dynamic",
            tags={"player"}
        )
        self.vx = 0.0
        self.vy = 0.0
        self.sprite = sprite

        # состояние рывка (таймеры)
        self._dash_timer: float = 0.0
        self._dash_cooldown_timer: float = 0.0
        self._dash_ui_timer: float = 0.0

        # подтягиваем статы из конфига
        self.max_speed = config.PLAYER_MAX_SPEED
        self.acceleration = config.PLAYER_ACCELERATION
        self.friction = config.PLAYER_FRICTION
        self.dash_speed = config.PLAYER_DASH_SPEED
        self.dash_cooldown = config.PLAYER_DASH_COOLDOWN
        self._max_dash_cooldown = self.dash_cooldown
        self.dash_duration = config.PLAYER_DASH_DURATION
        self.current_hp = config.UI_HP_MAX
        self.max_hp = config.UI_HP_MAX

        self.visual_offset_y = -config.PLAYER_SIZE // 2

        self.current_tilt = 0.0

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def render(self, surface: pygame.Surface) -> None:
        draw_x = self.rect.x
        draw_y = self.rect.y + self.visual_offset_y

        # отрисовка с учётом наклона
        if abs(self.current_tilt) > 0.5:  # порог
            rotated = pygame.transform.rotate(self.sprite, -self.current_tilt)

            # корректируем позицию чтобы нижний центр спрайта оставался на месте
            w_shift = (self.sprite.get_width() - rotated.get_width()) / 2
            h_shift = self.sprite.get_height() - rotated.get_height()

            surface.blit(rotated, (draw_x + w_shift, draw_y + h_shift))
        else:
            surface.blit(self.sprite, (draw_x, draw_y))

    def update(self, dx: float, dy: float, dt: float, dash_requested: bool) -> None:
        """
        dx, dy: Направление ввода
        dt: Delta time в секундах
        dash_requested - флаг отработки рывка
        """

        # обновляем таймер для кд
        if self._dash_cooldown_timer > 0:
            self._dash_cooldown_timer -= dt
        # обновляем таймер для ui
        if self._dash_ui_timer > 0:
            self._dash_ui_timer -= dt

        # делаем рывок (коли можем)
        if dash_requested and self._dash_cooldown_timer <= 0 and (dx != 0 or dy != 0):
            self._dash_timer = self.dash_duration
            self._dash_cooldown_timer = self.dash_cooldown
            self._dash_ui_timer = config.UI_DASH_HIDE_DELAY

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

        # нормализуем vx к диапазону [-1, 1] и умножаем на макс. угол
        tilt_ratio = self.vx / config.PLAYER_MAX_SPEED
        target_tilt = tilt_ratio * config.PLAYER_TILT_MAX_ANGLE

        # плавная интерполяция
        self.current_tilt += (target_tilt - self.current_tilt) * config.PLAYER_TILT_SMOOTHING * dt

        # ограничиваем диапазон
        self.current_tilt = max(-config.PLAYER_TILT_MAX_ANGLE,
                                min(config.PLAYER_TILT_MAX_ANGLE, self.current_tilt))

    @property
    def hp_ratio(self) -> float:
        return max(0.0, min(1.0, self.current_hp / self.max_hp))

    @property
    def dash_cooldown_ratio(self) -> float:
        if self._max_dash_cooldown <= 0: return 1.0
        return max(0.0, min(1.0, 1.0 - (self._dash_cooldown_timer / self._max_dash_cooldown)))

    @property
    def is_dash_ui_visible(self) -> bool:
        return self._dash_ui_timer > 0 or self._dash_cooldown_timer > 0
