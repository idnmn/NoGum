import math
import pygame
from pygame import Vector2
import config
from models.game_state import GameState
from skills.skill import Skill


# ближняя атака (аля добивание) для игрока
class Slash(Skill):
    def __init__(self, state: GameState) -> None:
        super().__init__(state)

        self.radius = config.SLASH_RADIUS
        self.angle_span = config.SLASH_ANGLE_SPAN
        self.damage =  config.SLASH_DAMAGE
        self.stun_time = config.SLASH_STUN_TIME
        self.attack_time = config.SLASH_ATTACK_TIME
        self._cool_down = config.SLASH_COOLDOWN

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
        self.indicator_background_color = config.UI_SLASH_BG_COLOR
        self.indicator_fill_color = config.UI_SLASH_COLOR
        self.indicator_sprite = self._state.assets['slash_ico']

    def render(self, surface: pygame.Surface) -> None:
        origin = Vector2(self._state.player.rect.center)
        end_pos = origin + Vector2(self.radius * 0.75).rotate(self._draw_angle)

        self._state.particle_system.spawn_slash(origin, end_pos, self.radius, self._facing_right)

        rotated_surface = pygame.transform.rotate(self.surface, -self.angle)

        # дебаг отрисовка
        if config.DRAW_SLASH:
            colored_surf = pygame.Surface(rotated_surface.get_size(), pygame.SRCALPHA)
            colored_surf.fill((*config.UI_DASH_COLOR, 100))

            temp_surf = rotated_surface.copy()
            temp_surf.set_colorkey((0, 0, 0))

            final_surf = rotated_surface.copy()
            final_surf.fill((*config.UI_DASH_COLOR, 128), special_flags=pygame.BLEND_RGBA_MULT)

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
        self._timer = self.attack_time

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

