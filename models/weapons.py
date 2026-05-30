import math
import random
import config
from dataclasses import dataclass
from models.projectile import *


@dataclass
class Weapon:
    name: str = ''
    sprite: pygame.Surface | None = None
    reload_sprite: pygame.Surface | None = None
    crosshair: pygame.Surface | None = None
    # Сдвиги для рендера
    offset_x: float = 0
    offset_y: float = 0
    facing_right: bool = True
    angle: float = 0

    is_reloading: bool = False
    reload_timer = 0.0
    reload_cooldown = 1.0

    is_autofired: bool = True

class Pointer(Weapon):
    def __init__(self, sprite: pygame.Surface, reload_sprite: pygame.Surface,
                 crosshair: pygame.Surface) -> None:
        super().__init__()
        self.sprite = sprite
        self.reload_sprite = reload_sprite
        self.crosshair = crosshair
        self.name = 'Pointer'
        self.offset_x = 15

        # балансировочные переменные
        """балансировочная формула:
            power = const; power = damage * fire_rate; damage = size * speed
            +speed = -fire_rate
            +size = -speed
            +fire_rate = -size"""
        self.bullet_size = 2.0 # px
        self.min_bullet_size = 2.0
        self.max_bullet_size = 0.0
        self._size_coef = 5.0

        self.fire_rate = 3.0
        self.min_fire_rate = 3.0
        self.max_fire_rate = 0.0
        self._fire_rate_coef = 1.0

        self.bullet_speed = 2.0
        self.min_bullet_speed = 2.0
        self.max_bullet_speed = 0.0
        self._speed_coef = 200.0

        self.power = 25
        self._damage_coef = 1.0
        self._calculate_max()

        self.clip_size = 5
        self.clip = 5

        self.level = 1
        self.upgrade_cost = 10
        self.can_upgrade = True

    def upgrade(self):
        self.level += 1
        if self.level % 2 == 0:
            self.upgrade_cost += 10
            self.power += 5
            
        if self.level % 4 == 0:
            self.clip_size += 5
            self._damage_coef += 0.05

        self._calculate_max()

        if self.power >= config.MAX_POWER_LIMIT:
            self.can_upgrade = False

    def _calculate_max(self) -> None:
        self.max_bullet_speed = round(self.power / (self.min_bullet_size * self.min_fire_rate), 0)
        self.max_bullet_size = round(self.power / (self.min_bullet_speed * self.min_fire_rate), 0)
        self.max_fire_rate = round(self.power / (self.min_bullet_size * self.min_bullet_speed), 1)

        self.fire_rate = round(self.power / (self.bullet_size * self.bullet_speed), 1)

    def change_speed(self, new_speed: float) -> None:
        delta = self.bullet_speed - new_speed
        if delta > 0: # уменьшение
            if new_speed < self.min_bullet_speed:
                self.bullet_speed = self.min_bullet_speed
            else:
                self.bullet_speed = new_speed

            if self.bullet_size < self.max_bullet_size:
                self.bullet_size = self.power / (self.bullet_speed * self.fire_rate)
            else:
                self.fire_rate = self.power / (self.bullet_speed * self.bullet_size)

        else: # увеличение
            if new_speed > self.max_bullet_speed:
                self.bullet_speed = self.max_bullet_speed
            else:
                self.bullet_speed = new_speed

            if self.fire_rate > self.min_fire_rate:
                self.fire_rate = self.power / (self.bullet_speed * self.bullet_size)
            else:
                self.bullet_size = self.power / (self.bullet_speed * self.fire_rate)

    def change_size(self, new_size: float) -> None:
        delta = self.bullet_size - new_size
        if delta > 0:  # уменьшение
            if new_size < self.min_bullet_size:
                self.bullet_size = self.min_bullet_size
            else:
                self.bullet_size = new_size

            if self.fire_rate < self.max_fire_rate:
                self.fire_rate = self.power / (self.bullet_speed * self.bullet_size)
            else:
                self.bullet_speed = self.power / (self.bullet_size * self.fire_rate)

        else:  # увеличение
            if new_size > self.max_bullet_size:
                self.bullet_size = self.max_bullet_size
            else:
                self.bullet_size = new_size

            if self.bullet_speed > self.min_bullet_speed:
                self.bullet_speed = self.power / (self.fire_rate * self.bullet_size)
            else:
                self.fire_rate = self.power / (self.bullet_speed * self.bullet_size)

    def change_fire_rate(self, new_fire_rate: float) -> None:
        delta = self.fire_rate - new_fire_rate
        if delta > 0:  # уменьшение
            if new_fire_rate < self.min_fire_rate:
                self.fire_rate = self.min_fire_rate
            else:
                self.fire_rate = new_fire_rate

            if self.bullet_speed < self.max_bullet_speed:
                self.bullet_speed = self.power / (self.fire_rate * self.bullet_size)
            else:
                self.bullet_size = self.power / (self.bullet_speed * self.fire_rate)

        else:  # увеличение
            if new_fire_rate > self.max_fire_rate:
                self.fire_rate = self.max_fire_rate
            else:
                self.fire_rate = new_fire_rate

            if self.bullet_size > self.min_bullet_size:
                self.bullet_size = self.power / (self.bullet_speed * self.fire_rate)
            else:
                self.bullet_speed = self.power / (self.fire_rate * self.bullet_size)

    def get_speed(self) -> float:
        return self.bullet_speed * self._speed_coef

    def get_size(self) -> float:
        return self.bullet_size * self._size_coef

    def get_fire_rate(self) -> float:
        return self.fire_rate * self._fire_rate_coef

    @property
    def damage(self) -> float:
        return self.bullet_speed * self.bullet_size * self._damage_coef

    def fire(self, projectile_system, state) -> None:
        offset_coef = self.offset_x + (self.bullet_size * self._size_coef) / 2

        origin = pygame.Vector2(state.player.rect.centerx, state.player.rect.centery)
        direction = state.player.mouse_world_pos - origin

        angle = random.randint(-3, 3)
        spawn_pos = origin + direction.rotate(angle).normalize() * offset_coef

        projectile_system.spawn(PointerProjectile, spawn_pos, direction.rotate(angle))

    # отрисовка
    def render(self, surface: pygame.Surface,
               mouse_world_pos: pygame.Vector2, player_pos: pygame.Vector2) -> None:
        # обычное отображение
        if not self.is_reloading:
            dx = mouse_world_pos.x - player_pos.x
            dy = mouse_world_pos.y - player_pos.y
            angle = math.degrees(math.atan2(dy, dx))

            # зеркалирование
            weapon_sprite = self.sprite
            offset_x = self.offset_x
            if not self.facing_right:
                weapon_sprite = pygame.transform.flip(self.sprite, False, True)
                offset_x = -offset_x

            # вращаем спрайт оружия
            rotated = pygame.transform.rotate(weapon_sprite, -angle)


        # анимация перезарядки
        else:
            self.angle += 20

            # зеркалирование
            weapon_sprite = self.reload_sprite
            offset_x = self.offset_x
            if not self.facing_right:
                weapon_sprite = pygame.transform.flip(self.sprite, False, True)
                offset_x = -offset_x

            # вращаем спрайт оружия
            rotated = pygame.transform.rotate(weapon_sprite, -self.angle)

        # позиционируем оружие
        wx = player_pos.x - rotated.get_width() / 2 + offset_x
        wy = player_pos.y - rotated.get_height() / 2 + self.offset_y

        surface.blit(rotated, (wx, wy))
