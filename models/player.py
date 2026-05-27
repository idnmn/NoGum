import math
import pygame
from pygame import Vector2

import config
from models.collidable import CollisionBody
from models.game_state import GameState
from models.renderable import Renderable
from models.weapons import Weapon
from models.decal import Decal
from services.decal_system import DecalSystem


class Player(Renderable):
    def __init__(self, x: float, y: float, sprite: pygame.Surface, step_sprite: pygame.Surface,
                 state: GameState) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, config.PLAYER_SIZE, config.PLAYER_SIZE),
            layer="dynamic",
            tags={"player"}
        )
        self._state = state

        self._source_sprite = sprite
        self.sprite = sprite
        self.step_sprite = step_sprite

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

        self.is_alive = True

        self.visual_offset_y = -config.PLAYER_SIZE // 2

        self.current_tilt = 0.0
        self.step_offset = False
        self.step_cooldown = 0.07
        self._step_timer = 0.0

        self.weapon: Weapon | None = None
        self.mouse_world_pos = pygame.Vector2(x, y)
        self.facing_right = True

        self._visual_damage_cooldown = 0.2
        self._visual_damage_timer = -1.0

    def set_mouse_pos(self, pos: tuple[float, float]) -> None:
        self.mouse_world_pos.update(pos)
        self.facing_right = self.mouse_world_pos.x >= self.rect.centerx
        self.weapon.facing_right = self.facing_right

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
            self.weapon.render(surface, self.mouse_world_pos, Vector2(self.rect.center))

    # Отрисовка шагов
    def _draw_step(self, decals_system: DecalSystem) -> None:
        offset_x, offset_y = 0, 0
        if self.body.vx:
            if self.step_offset:
                offset_y = 15
            else:
                offset_y = 0
        if self.body.vy:
            if self.step_offset:
                offset_x = 15
            else:
                offset_x = 0
        elif self.body.vx == 0 and self.body.vy == 0:
            return
        offset = Vector2(offset_x, offset_y) + Vector2(10, 10)
        self.step_offset = not self.step_offset

        step = Decal(
            pos=Vector2(self.rect.x, self.rect.y) + offset,
            lifetime=1.5,
            size_x=12,
            size_y=12,
            sprite=self.step_sprite,
            fade_time=0.5,
            max_alpha=150
        )

        decals_system.decals.append(step)

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

        # обновляем таймер шагов
        if self._step_timer > 0:
            self._step_timer -= dt

        # обновляем таймер визуализации урона
        if self._visual_damage_timer > 0:
            self.sprite.fill((255, 0, 0, 0), None, pygame.BLEND_RGB_ADD)
            self._visual_damage_timer -= dt

        if self._visual_damage_timer <= 0:
            self.sprite = self._source_sprite.copy()

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

        # рисуем следы
        if self._step_timer <= 0:
            self._draw_step(self._state.decals_system)
            self._step_timer = self.step_cooldown

        # нормализуем vx к диапазону [-1, 1] и умножаем на макс. угол
        tilt_ratio = self.body.vx / config.PLAYER_MAX_SPEED
        target_tilt = tilt_ratio * config.PLAYER_TILT_MAX_ANGLE

        # плавная интерполяция
        self.current_tilt += (target_tilt - self.current_tilt) * config.PLAYER_TILT_SMOOTHING * dt

        # ограничиваем диапазон наклона
        self.current_tilt = max(-config.PLAYER_TILT_MAX_ANGLE,
                                min(config.PLAYER_TILT_MAX_ANGLE, self.current_tilt))

    def take_damage(self, amount: float) -> None:
        self.hp -= int(amount)

        self._state.camera.shake(3, 0.15)

        self._visual_damage_timer = self._visual_damage_cooldown
        self.sprite.fill((255, 0, 0, 0), None, pygame.BLEND_RGBA_ADD)
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
