import math
import pygame
import config
from models.collidable import CollisionBody
from models.renderable import Renderable
from models.weapons import Weapon


class Player(Renderable):
    def __init__(self, x: float, y: float, sprite: pygame.Surface) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, config.PLAYER_SIZE, config.PLAYER_SIZE),
            layer="dynamic",
            tags={"player"}
        )
        self.sprite = sprite

        # состояние рывка (таймеры)
        self._dash_timer: float = 0.0
        self._dash_cooldown_timer: float = 0.0
        self._dash_ui_timer: float = 0.0

        # подтягиваем статы из конфига
        self.max_speed = config.PLAYER_MAX_SPEED
        self.acceleration = config.PLAYER_ACCELERATION
        self.friction = config.FRICTION
        self.dash_speed = config.PLAYER_DASH_SPEED
        self.dash_cooldown = config.PLAYER_DASH_COOLDOWN
        self._max_dash_cooldown = self.dash_cooldown
        self.dash_duration = config.PLAYER_DASH_DURATION
        self.hp = config.UI_HP_MAX
        self.max_hp = config.UI_HP_MAX


        self.immunity_duration = 0.5
        self._immunity_timer = 0.0
        self.in_immunity = False
        self.is_alive = True

        self.visual_offset_y = -config.PLAYER_SIZE // 2

        self.current_tilt = 0.0

        self.weapon: Weapon | None = None
        self.mouse_world_pos = pygame.Vector2(x, y)
        self.facing_right = True

    def set_mouse_pos(self, pos: tuple[float, float]) -> None:
        self.mouse_world_pos.update(pos)
        self.facing_right = self.mouse_world_pos.x >= self.rect.centerx

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def render(self, surface: pygame.Surface) -> None:
        draw_x = self.rect.x
        draw_y = self.rect.y + self.visual_offset_y

        # зеркалирование (педалирование) спрайта
        player_sprite = self.sprite
        if not self.facing_right:
            player_sprite = pygame.transform.flip(self.sprite, True, False)

        # отрисовка с учётом наклона
        if abs(self.current_tilt) > 0.5:  # порог
            rotated = pygame.transform.rotate(player_sprite, -self.current_tilt)

            # корректируем позицию чтобы нижний центр спрайта оставался на месте
            w_shift = (self.sprite.get_width() - rotated.get_width()) / 2
            h_shift = self.sprite.get_height() - rotated.get_height()

            surface.blit(rotated, (draw_x + w_shift, draw_y + h_shift))
        else:
            surface.blit(player_sprite, (draw_x, draw_y))

        # отрисовка оружия поверх персонажа
        if self.weapon and self.weapon.sprite:
            self._draw_weapon(surface)

    # отрисовка оружия
    def _draw_weapon(self, surface: pygame.Surface) -> None:
        dx = self.mouse_world_pos.x - self.rect.centerx
        dy = self.mouse_world_pos.y - self.rect.centery
        angle = math.degrees(math.atan2(dy, dx))

        # зеркалирование
        weapon_sprite = self.weapon.sprite
        offset_x = self.weapon.offset_x
        if not self.facing_right:
            weapon_sprite = pygame.transform.flip(self.weapon.sprite, False, True)
            offset_x = -offset_x

        # вращаем спрайт оружия
        rotated = pygame.transform.rotate(weapon_sprite, -angle)

        # позиционируем оружие
        wx = self.rect.centerx - rotated.get_width() / 2 + offset_x
        wy = self.rect.centery - rotated.get_height() / 2 + self.weapon.offset_y
        surface.blit(rotated, (wx, wy))

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

        # обновляем таймер неуязвимости
        if self._immunity_timer > 0:
            self._immunity_timer -= dt
        if self._immunity_timer <= 0:
            self.in_immunity = False


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
            self.body.vx *= damping
            self.body.vy *= damping

        # интегрируем ускорение в скорость
        self.body.vx += ax * dt
        self.body.vy += ay * dt

        # ограничиваем максимальную скорость
        current_speed = self.body.velocity.magnitude()
        if current_speed > self.max_speed:
            scale = current_max_speed / current_speed
            self.body.vx *= scale
            self.body.vy *= scale

        # защита от дрейфа
        if current_speed < 2.0:
            self.body.vx = 0.0
            self.body.vy = 0.0

        # обновляем позицию
        self.body.rect.x += self.body.vx * dt
        self.body.rect.y += self.body.vy * dt

        # нормализуем vx к диапазону [-1, 1] и умножаем на макс. угол
        tilt_ratio = self.body.vx / config.PLAYER_MAX_SPEED
        target_tilt = tilt_ratio * config.PLAYER_TILT_MAX_ANGLE

        # плавная интерполяция
        self.current_tilt += (target_tilt - self.current_tilt) * config.PLAYER_TILT_SMOOTHING * dt

        # ограничиваем диапазон
        self.current_tilt = max(-config.PLAYER_TILT_MAX_ANGLE,
                                min(config.PLAYER_TILT_MAX_ANGLE, self.current_tilt))

    def take_damage(self, amount: float) -> None:
        if not self.in_immunity:
            self.in_immunity = True
            self._immunity_timer = self.immunity_duration
            self.hp -= amount
            if self.hp <= 0:
                self.is_alive = False

    @property
    def hp_ratio(self) -> float:
        return max(0.0, min(1.0, self.hp / self.max_hp))

    @property
    def dash_cooldown_ratio(self) -> float:
        if self._max_dash_cooldown <= 0: return 1.0
        return max(0.0, min(1.0, 1.0 - (self._dash_cooldown_timer / self._max_dash_cooldown)))

    @property
    def is_dash_ui_visible(self) -> bool:
        return self._dash_ui_timer > 0 or self._dash_cooldown_timer > 0
