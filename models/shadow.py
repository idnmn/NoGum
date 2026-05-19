import pygame
from pygame import Vector2

from models.collidable import CollisionBody
from models.renderable import Renderable


class Shadow(Renderable):
    def __init__(self, owner: CollisionBody) -> None:
        self.x = owner.rect.x
        self.y = int(owner.rect.y + owner.rect.height / 1.2)
        self.size_x = owner.rect.width
        self.size_y = owner.rect.height
        self.owner = owner

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.size_x / 2, self.y  - self.size_y / 2,
                           self.size_x, self.size_y)

    def update(self):
        self.x = self.owner.rect.x
        self.y = int(self.owner.rect.y + self.owner.rect.height / 1.2)

    def render(self, surface: pygame.Surface, room_offset: Vector2) -> None:
        x, y = Vector2(self.x, self.y) - room_offset + Vector2(0, self.owner.shadow_offset)
        pygame.draw.ellipse(surface, (0, 0, 0, 100), (x, y, self.size_x, self.size_y / 2))
