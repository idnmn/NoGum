import pygame
from models.collidable import CollisionBody


# Переход на следующий этаж
class Exit():
    def __init__(self, x: float, y: float, size: int,
                 sprite: pygame.Surface, arrow_sprite: pygame.Surface) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, size, size),
            layer="static",
            tags={"exit"}
        )

        self.interactive_hitbox = CollisionBody(
            rect=pygame.Rect(x - size * 0.5, y - size * 0.5, size * 2, size * 2),
            layer="interactive",
            tags={"exit"}
        )

        self._sprite = sprite
        self.arrow_sprite = arrow_sprite

        self.is_near_player = False

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self._sprite, (self.rect.x, self.rect.y))

        if self.is_near_player:
            surface.blit(self.arrow_sprite, (self.body.rect.x + self.body.rect.width / 2 - 24,
                                             self.body.rect.y - 30))
