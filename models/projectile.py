import pygame
from models.collidable import CollisionBody
from models.renderable import Renderable


class Projectile(Renderable):
    def __init__(self, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"projectile", "player_owner"}
        )
        self.velocity = velocity
        self.damage = damage
        self.lifetime = lifetime
        self.is_active = True

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

class PointerProjectile(Projectile):
    def __init__(self, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0) -> None:
        super().__init__(x, y, size, velocity, damage, lifetime)

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (110, 190, 130), self.rect.center, self.rect.width // 2)
        pygame.draw.circle(surface, (155, 255, 135), self.rect.center, (self.rect.width // 2) * 0.8)