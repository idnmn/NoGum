import pygame
import math
from pygame import Vector2
from configs import config, skills_stats
from models.enemies import Enemy
from models.game_state import GameState
from models.projectile import ZapProjectile


# общий шаблон класса для способностей
class Skill():
    def __init__(self, state: GameState) -> None:
        self._state = state
        self.hitbox = state.player.rect.copy()

        self._cool_down = 0.0
        self.cool_down_coef = 1.0
        self._cooldown_timer = 0.0
        self._use_timer = 0.0

        self.charges_count = 1
        self.max_charges = 1

        self.is_using = False
        self.is_ready = True

        # констранты для рендера индикатора
        self.indicator_background_color = (30, 30, 30)
        self.indicator_fill_color = (220, 220, 220)

    def update(self, dt: float) -> None:
        self._cooldown_timer -= dt
        self._use_timer -= dt

        if self._use_timer <= 0 and self.is_using:
            self.ended()

        if self._cooldown_timer <= 0 and not self.is_using and self.charges_count < self.max_charges:
            self.charges_count += 1
            self.is_ready = True
            if self.max_charges != 1:
                self._state.audio_manager.play_sound('skill_get_charge')
                self._cooldown_timer = self._cool_down

            if self.charges_count == self.max_charges:
                self.reload()
            else:
                self._cooldown_timer = self.cool_down

        self.hitbox.x = self._state.player.rect.x
        self.hitbox.y = self._state.player.rect.y

    def render(self, surface: pygame.Surface) -> None:
        pass

    def reload(self) -> None:
        self._state.audio_manager.play_sound('skill_reloaded')

    def ended(self) -> None:
        self.is_using = False
        if self.charges_count == 0:
            self.is_ready = False
        if self._cooldown_timer <= 0:
            self._cooldown_timer = self.cool_down

    def use(self, mouse_pos: Vector2) -> None:
        self.is_using = True
        self.charges_count -= 1

    @property
    def cool_down(self) -> float:
        return self._cool_down * self.cool_down_coef

    @property
    def cooldown_ratio(self):
        return max(0.0, min(1.0, 1.0 - (self._cooldown_timer / (self.cool_down))))

    def on_enemy_collide(self, enemy: Enemy):
        pass


# ближняя атака (аля добивание) для игрока
class Slash(Skill):
    def __init__(self, state: GameState) -> None:
        super().__init__(state)

        self.radius = skills_stats.SLASH_RADIUS
        self.angle_span = skills_stats.SLASH_ANGLE_SPAN
        self.damage =  skills_stats.SLASH_DAMAGE
        self.stun_time = skills_stats.SLASH_STUN_TIME
        self.attack_time = skills_stats.SLASH_ATTACK_TIME
        self._cool_down = skills_stats.SLASH_COOLDOWN

        self.max_charges = 2
        self.charges_count = 2

        size = self.radius * 2 + 10
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)

        center = (size // 2, size // 2)
        points = [center]

        # генерируем точки дуги
        start_angle = -self.angle_span / 2
        end_angle = self.angle_span / 2
        steps = 20  # шакальность дуги

        for i in range(steps + 1):
            rad = math.radians(start_angle + (end_angle - start_angle) * (i / steps))
            x = center[0] + self.radius * math.cos(rad)
            y = center[1] + self.radius * math.sin(rad)
            points.append((x, y))

        pygame.draw.polygon(self.surface, (255, 255, 255), points)

        self.base_mask = pygame.mask.from_surface(self.surface)
        self.mask = pygame.mask.from_surface(self.surface)
        self.rect = self.surface.get_rect(center=center)
        self.angle = 0.0
        self._draw_angle = 0.0
        self.pivot_offset = pygame.Vector2(15)
        self._facing_right = False

        # констранты для рендера индикатора
        self.indicator_background_color = skills_stats.UI_SLASH_BG_COLOR
        self.indicator_fill_color = skills_stats.UI_SLASH_COLOR
        self.indicator_sprite = self._state.assets['slash_ico']

    def render(self, surface: pygame.Surface) -> None:
        origin = Vector2(self._state.player.rect.center)
        end_pos = origin + Vector2(self.radius * 0.75).rotate(self._draw_angle)

        self._state.particle_system.spawn_slash(origin, end_pos, self.radius, self._facing_right)

        rotated_surface = pygame.transform.rotate(self.surface, -self.angle)

        # дебаг отрисовка
        if config.DRAW_SLASH:
            colored_surf = pygame.Surface(rotated_surface.get_size(), pygame.SRCALPHA)
            colored_surf.fill((*self._state.player.signature_color, 100))

            temp_surf = rotated_surface.copy()
            temp_surf.set_colorkey((0, 0, 0))

            final_surf = rotated_surface.copy()
            final_surf.fill((*self._state.player.signature_color, 128), special_flags=pygame.BLEND_RGBA_MULT)

            rect = final_surf.get_rect(center=self._state.player.rect.center)
            surface.blit(final_surf, rect)

    def update(self, dt: float) -> None:
        super().update(dt)

        for enemy in self._state.enemy_system.enemies:
            if enemy.hp - (self.damage - enemy.defence) <= 0:
                enemy.slash_marked = True

        if self.is_using:
            if self._facing_right:
                self._draw_angle += (dt / self.attack_time) * self.angle_span
            else:
                self._draw_angle -= (dt / self.attack_time) * self.angle_span

    def use(self, mouse_pos: Vector2) -> None:
        super().use(mouse_pos)

        self._state.camera.shake(20, self.attack_time)
        self._use_timer = self.attack_time

        mouse_pos += self._state.room_manager.active_room.offset
        dx = mouse_pos[0] - self._state.player.rect.centerx
        dy = mouse_pos[1] - self._state.player.rect.centery

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        rotated_surface = pygame.transform.rotate(self.surface, -angle_deg)

        rotated_mask = pygame.mask.from_surface(rotated_surface)

        rotated_rect = rotated_surface.get_rect()
        rotated_rect.center = self._state.player.rect.center

        self.rect = rotated_rect
        self.mask = rotated_mask
        self.angle = angle_deg

        self._draw_angle = (self.angle)
        if self._state.player.facing_right:
            self._facing_right = True
            self._draw_angle -= self.angle_span
        else:
            self._facing_right = False

        # хитуем врагов и помечаем врагов
        for enemy in self._state.enemy_system.enemies:
            if self.mask.overlap(enemy.mask, (enemy.rect.x - self.rect.x, enemy.rect.y - self.rect.y)):
                enemy.take_damage(self.damage)

                if enemy.hp > 0:
                    enemy.state = 'stun'
                    enemy._state_timer = self.stun_time

                else:
                    enemy.slash_killed = True

                self._state.particle_system.spawn_dashed(enemy.rect.center)

                enemy.body.vx = 0
                enemy.body.vy = 0

                self._state.audio_manager.play_sound('slash_hit', 1.2)
        self._state.audio_manager.play_sound('slash', 2)


# стандартный рывок
class StandardDash(Skill):
    def __init__(self, state: GameState) -> None:
        super().__init__(state)

        self.speed = skills_stats.STANDARD_DASH_SPEED
        self._cool_down = skills_stats.STANDARD_DASH_COOLDOWN
        self.duration = skills_stats.STANDARD_DASH_DURATION
        self._ui_timer: float = 0.0

        # фиксируем направление игрока в начале рывка
        self.dx = 0.0
        self.dy = 0.0

        # констранты для рендера индикатора
        self.indicator_background_color = skills_stats.UI_DASH_BG_COLOR
        self.indicator_fill_color = skills_stats.UI_DASH_COLOR
        self.indicator_sprite = self._state.assets['dash_ico']


    def update(self, dt: float) -> None:
        super().update(dt)

        if self.is_using:
            self._state.particle_system.spawn_while_dash(self._state.player.rect.center, Vector2(self._state.player.body.dx,
                                                                                           self._state.player.body.dy),
                                                         self._state.player.signature_color, config.PLAYER_SIZE)
            # фиксируем направление игрока
            self._state.player.body.dx, self._state.player.body.dy = self.dx, self.dy

    def reload(self) -> None:
        super().reload()
        self._state.particle_system.spawn_dash_reloaded(self._state.player.rect.center)

    def ended(self) -> None:
        super().ended()

        # сбрасываем ускорение
        self._state.player.acceleration //= 100
        self._state.player.current_max_speed = self._state.player.max_speed
        self._state.player.ignore_enemy = False

    def use(self, mouse_pos: Vector2) -> None:
        if self._state.player.body.ax != 0 or self._state.player.body.ay != 0:
            self.dx, self.dy = Vector2(self._state.player.body.ax, self._state.player.body.ay).normalize()
            super().use(mouse_pos)

            self._use_timer = self.duration

            self._state.particle_system.spawn_dashed(self._state.player.rect.center)

            # ускоряем игрока
            self._state.player.acceleration *= 100
            self._state.player.current_max_speed = self.speed
            self._state.player.ignore_enemy = True

            self._state.audio_manager.play_sound('dash')


# магнитный рывок
class MagnetDash(Skill):
    def __init__(self, state: GameState) -> None:
        super().__init__(state)

        px, py = state.player.rect.x, state.player.rect.y
        w, h = state.player.rect.width * 3, state.player.rect.height * 3
        self.hitbox = pygame.rect.Rect(px - w // 2, py // 2, w, h)

        self.min_damage = skills_stats.MAGNET_MIN_DAMAGE
        self.max_damage = skills_stats.MAGNET_MAX_DAMAGE
        self.speed = skills_stats.MAGNET_DASH_SPEED
        self._cool_down = skills_stats.MAGNET_DASH_COOLDOWN
        self.duration = skills_stats.MAGNET_DASH_DURATION
        self.max_charges = 3
        self.charges_count = 3
        self._ui_timer: float = 0.0
        self.damage_coef = 0.2

        # фиксируем направление игрока в начале рывка
        self.dx = 0.0
        self.dy = 0.0

        # констранты для рендера индикатора
        self.indicator_background_color = skills_stats.UI_MAGNET_BG_COLOR
        self.indicator_fill_color = skills_stats.UI_MAGNET_COLOR
        self.indicator_sprite = self._state.assets['dash_ico']


    def update(self, dt: float) -> None:
        super().update(dt)

        if self.is_using:
            self._state.particle_system.spawn_magnet_dash_trail(self._state.player.rect.center,
                                                         self._state.player.signature_color, config.PLAYER_SIZE)
            # фиксируем направление игрока
            self._state.player.body.dx, self._state.player.body.dy = self.dx, self.dy

        self.hitbox.x -= self.hitbox.width // 2
        self.hitbox.y -= self.hitbox.height // 2

    def reload(self) -> None:
        super().reload()
        self._state.particle_system.spawn_dash_reloaded(self._state.player.rect.center,
                                                        self._state.player.signature_color)

    def ended(self) -> None:
        super().ended()

        # сбрасываем ускорение
        self._state.player.acceleration //= 100
        self._state.player.current_max_speed = self._state.player.max_speed
        self._state.player.ignore_enemy = False

    def use(self, mouse_pos: Vector2) -> None:
        mouse_pos += self._state.room_manager.active_room.offset
        self.dx = mouse_pos[0] - self._state.player.rect.centerx
        self.dy = mouse_pos[1] - self._state.player.rect.centery
        super().use(mouse_pos)

        self._use_timer = self.duration

        self._state.particle_system.spawn_magnet_dashed(self._state.player.rect.center)

        # ускоряем игрока
        self._state.player.acceleration *= 100
        self._state.player.current_max_speed = self.speed
        self._state.player.ignore_enemy = True

        self._state.audio_manager.play_sound('dash')

    def on_enemy_collide(self, enemy: Enemy):
        if enemy.status_manager.electrified and self.is_using:
            damage = min(self.max_damage, max(self.min_damage, self.damage_coef * enemy.status_manager.electrified))

            enemy.take_damage(damage)
            self._state.audio_manager.play_sound('magnet_hit', 1.2)
            self._state.particle_system.spawn_magnet_hitted(enemy.rect.center)


# электро заряд
class Zap(Skill):
    def __init__(self, state: GameState) -> None:
        super().__init__(state)

        self.speed = skills_stats.ZAP_SPEED
        self.electrified = skills_stats.ZAP_ELECTRIFIED
        self.stun_time = skills_stats.ZAP_STUN_TIME
        self._cool_down = skills_stats.ZAP_COOLDOWN

        self.max_charges = 1
        self.charges_count = 1

        # констранты для рендера индикатора
        self.indicator_background_color = skills_stats.UI_ZAP_BG_COLOR
        self.indicator_fill_color = skills_stats.UI_ZAP_COLOR
        self.indicator_sprite = self._state.assets['zap_ico']

    def reload(self) -> None:
        super().reload()
        self._state.audio_manager.play_sound('zap_reloaded', 1.8)

    def update(self, dt: float) -> None:
        super().update(dt)

    def use(self, mouse_pos: Vector2) -> None:
        super().use(mouse_pos)

        self._state.camera.shake(20, 0.1)
        self._use_timer = 0.0

        mouse_pos += self._state.room_manager.active_room.offset
        dx = mouse_pos[0] - self._state.player.rect.centerx
        dy = mouse_pos[1] - self._state.player.rect.centery
        dir = Vector2(dx, dy).normalize()
        vel = dir * self.speed

        offset_coef = self._state.weapon.sprite.get_width() - self._state.weapon.offset_x * 3
        spawn_pos = self._state.player.rect.center + dir.normalize() * offset_coef

        self._state.projectile_system.projectiles.append(ZapProjectile(
            state=self._state,
            x=spawn_pos.x, y=spawn_pos.y,
            size=30,
            velocity=vel,
            electrified=self.electrified,
            lifetime=10.0
        ))

        self._state.audio_manager.play_sound('zap', 2)