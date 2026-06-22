import math
import random
import pygame
from pygame import Vector2
import config
from models.collidable import CollisionBody
from models.game_state import GameState
from models.weapons import Weapon
from models.decal import Decal
from skills.slash import Slash
from skills.standard_dash import StandardDash


class Player():
    def __init__(self, x: float, y: float, state: GameState) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, config.PLAYER_SIZE, config.PLAYER_SIZE),
            layer="dynamic",
            tags={"player"}
        )
        self._state = state
        self.first_skill = StandardDash(state)
        self.second_skill = Slash(state)

        self._source_sprite = state.assets['slasher_sprite']
        self.sprite = self._source_sprite.copy()
        self.step_sprite = state.assets['player_step_sprite']

        # подтягиваем статы из конфига
        self.max_speed = config.PLAYER_MAX_SPEED
        self.current_max_speed = config.PLAYER_MAX_SPEED
        self.acceleration = config.PLAYER_ACCELERATION
        self.friction = config.FRICTION
        self.hp = config.PLAYER_MAX_HP
        self.max_hp = config.PLAYER_MAX_HP
        self.tick_damage = config.PLAYER_TICK_DAMAGE
        self.tick_damage_coef = config.PLAYER_TICK_DAMAGE_COEF

        self.is_alive = True
        self.ignore_enemy = False

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

        self._tick_damage_timer = 3
        self._tick_damage_cooldown = 3

        # счетчик обломков в кармане
        self.scrap = 0

        # другие предметы
        self.inventory = dict()

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

        # отрисовка скилов
        if self.first_skill.is_using:
            self.first_skill.render(surface)

        if self.second_skill.is_using:
            self.second_skill.render(surface)

    # Отрисовка шагов
    def _draw_step(self) -> None:
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

        self._state.decals_system.decals.append(step)
        self._state.audio_manager.play_sound('player_walk')

    def update(self, dx: float, dy: float, dt: float) -> None:
        """
        dx, dy: Направление ввода
        dt: Delta time в секундах
        """
        self.body.dx = dx
        self.body.dy = dy

        # обновление скиллов
        self.first_skill.update(dt)
        self.second_skill.update(dt)

        # обновляем таймер шагов
        if self._step_timer > 0:
            self._step_timer -= dt

        # таймер утекающего здоровья
        if self._tick_damage_timer > 0:
            self._tick_damage_timer -= dt

        if self._tick_damage_timer <= 0:
            self._tick_damage_timer = self._tick_damage_cooldown
            self.take_damage(self.tick_damage * self.tick_damage_coef)

        # обновляем таймер визуализации урона
        if self._visual_damage_timer > 0:
            self.sprite.fill((255, 0, 0, 0), None, pygame.BLEND_RGB_ADD)
            self._visual_damage_timer -= dt

        if self._visual_damage_timer <= 0:
            self.sprite = self._source_sprite.copy()

        # вычисляем ускорение по направлению
        if self.body.dx != 0.0 or self.body.dy != 0.0:
            length = math.hypot(self.body.dx, self.body.dy)
            self.body.ax = (self.body.dx / length) * self.acceleration
            self.body.ay = (self.body.dy / length) * self.acceleration
        else:
            self.body.ax = self.body.ay = 0.0
            # применяем трение
            damping = math.exp(-self.friction * dt)
            self.body.vx *= damping
            self.body.vy *= damping

        # интегрируем ускорение в скорость
        self.body.vx += self.body.ax * dt
        self.body.vy += self.body.ay * dt

        # ограничиваем максимальную скорость
        current_speed = self.body.velocity.magnitude()
        if current_speed > self.current_max_speed:
            scale = self.current_max_speed / current_speed
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
            self._draw_step()
            self._step_timer = self.step_cooldown

        # нормализуем vx к диапазону [-1, 1] и умножаем на макс. угол
        tilt_ratio = self.body.vx / config.PLAYER_MAX_SPEED
        target_tilt = tilt_ratio * config.PLAYER_TILT_MAX_ANGLE

        # плавная интерполяция
        self.current_tilt += (target_tilt - self.current_tilt) * config.PLAYER_TILT_SMOOTHING * dt

        # ограничиваем диапазон наклона
        self.current_tilt = max(-config.PLAYER_TILT_MAX_ANGLE,
                                min(config.PLAYER_TILT_MAX_ANGLE, self.current_tilt))

    def take_damage(self, amount: float, no_shake: bool = False) -> None:
        self.hp -= int(amount)

        if not no_shake:
            self._state.camera.shake(5, 0.15)

        self._state.particle_system.spawn_player_damaged(self.body.rect.center)

        self._visual_damage_timer = self._visual_damage_cooldown
        self.sprite.fill((255, 0, 0, 0), None, pygame.BLEND_RGBA_ADD)
        if self.hp <= 0:
            self.is_alive = False
            self.death()

        self._state.stattracker.damage_taken += int(amount)

        self._state.audio_manager.play_sound(f'player_damaged_{random.randint(1, 3)}', 1.2)

    def death(self) -> None:
        self._state.reset_state()
        self._state.menu_manager.set_active_screen(self._state.menu_screens['main_menu'])

        self._state.stattracker.save_run()

    @property
    def hp_ratio(self) -> float:
        return max(0.0, min(1.0, self.hp / self.max_hp))
