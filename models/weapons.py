import pygame
import random
from dataclasses import dataclass
from models.projectile import *


@dataclass
class Weapon:
    name: str = ''
    sprite: pygame.Surface | None = None
    crosshair: pygame.Surface | None = None
    # Сдвиги для рендера
    offset_x: float = 0
    offset_y: float = 0
    # modules: list[Module] = field(default_factory=list)  # ← Зарезервировано для будущего

class Pointer(Weapon):
    def __init__(self, sprite: pygame.Surface | None = None, crosshair: pygame.Surface | None = None) -> None:
        super().__init__()
        self.sprite = sprite
        self.crosshair = crosshair
        self.name = 'Pointer'
        self.offset_x = 15

        # балансировочные переменные
        """балансировочная формула:
            power = const; power = damage * fire_rate; damage = size * speed
            +speed = -fire_rate
            +size = -speed
            +fire_rate = -size"""
        self.bullet_size = 5.0 # px
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
        self._speed_coef = 300.0

        self.power = 50
        self._damag_coef = 1.0
        self._calculate_max()

    def _calculate_max(self) -> None:
        self.max_bullet_speed = round(self.power / (self.min_bullet_size * self.min_fire_rate), 0)
        self.max_bullet_size = round(self.power / (self.min_bullet_speed * self.min_fire_rate), 0)
        self.max_fire_rate = round(self.power / (self.min_bullet_size * self.min_bullet_speed), 1)

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
        return self.bullet_speed * self.bullet_size * self._damag_coef

    def fire(self, projectile_system, state) -> None:
        origin = pygame.Vector2(state.player.body.center)
        direction = state.player.mouse_world_pos - origin

        angle = random.randint(-3, 3)

        projectile_system.spawn(PointerProjectile, origin, direction.rotate(angle), state.weapon)
