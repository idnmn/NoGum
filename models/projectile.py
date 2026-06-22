import pygame
import math

from models.collidable import CollisionBody


class Projectile():
    def __init__(self, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"projectile"}
        )
        self.velocity = velocity
        self.damage = damage
        self.lifetime = lifetime
        self.is_active = True

    def update(self, dt: float) -> None:
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        self.lifetime -= dt

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

class PointerProjectile(Projectile):
    def __init__(self, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0) -> None:
        super().__init__(x, y, size, velocity, damage, lifetime)
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"projectile", "player_owner"}
        )

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (110, 190, 130), self.rect.center, self.rect.width // 2)
        pygame.draw.circle(surface, (155, 255, 135), self.rect.center, (self.rect.width // 2) * 0.8)

class TazerProjectile(Projectile):
    def __init__(self, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0) -> None:
        super().__init__(x, y, size, velocity, damage, lifetime)
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"projectile", "player_owner"}
        )

        self._time_param = 0.0

    def update(self, dt: float) -> None:
        self._time_param += dt * 20
        self._time_param = self._time_param % 360

        offset_vector = (self.velocity.normalize().rotate(90) * (5 + (self.velocity.magnitude() / 70))
                         ** 0.5 * math.cos(self._time_param))

        self.rect.x += self.velocity.x * dt + offset_vector.x
        self.rect.y += self.velocity.y * dt + offset_vector.y

        self.lifetime -= dt

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (155, 240, 255), self.rect)
