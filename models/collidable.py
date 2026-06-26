import pygame
from dataclasses import dataclass, field
from typing import Set

from pygame import Vector2


@dataclass
class CollisionBody:
    rect: pygame.Rect
    layer: str = "default"      # для фильтрации (dynamic, static, trigger)
    tags: Set[str] = field(default_factory=set)  # для логики (player, enemy, wall)
    vx: float = 0.0
    vy: float = 0.0
    dx: float = 0.0
    dy: float = 0.0
    ax: float = 0.0
    ay: float = 0.0
    max_speed: float = 0.0
    current_max_speed: float = 0.0
    have_shadow: bool = False
    shadow_offset: float = 0.0
    impulse: Vector2 = field(default_factory=Vector2)

    @property
    def velocity(self):
        return Vector2(self.vx, self.vy)

    @property
    def center(self) -> tuple[float, float]:
        return self.rect.center
