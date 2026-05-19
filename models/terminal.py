import pygame
from pygame import Vector2

from models.collidable import CollisionBody
from models.renderable import Renderable


# местные телепорты
class Terminal(Renderable):
    def __init__(self, x: float, y: float, size: int,
                 sprite_active: pygame.Surface, sprite_inactive: pygame.Surface) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, size, size),
            layer="static",
            tags={"terminal"}
        )
        self.body.shadow_offset = -7

        self.interactive_hitbox = CollisionBody(
            rect=pygame.Rect(x - size, y - size, size * 3, size * 3),
            layer="interactive",
            tags={"terminal"}
        )

        self.sprite_active = sprite_active.copy().convert_alpha()
        self.sprite_inactive = sprite_inactive.copy().convert_alpha()
        self.visual_offset_y = -(sprite_active.get_height() - size)

        self.is_active = False
        self.is_near_player = False

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def render(self, surface: pygame.Surface) -> None:
        draw_x = self.rect.x
        draw_y = self.rect.y + self.visual_offset_y

        # отрисовываем спрайт
        if self.is_active:
            surface.blit(self.sprite_active, (draw_x, draw_y))
        else:
            surface.blit(self.sprite_inactive, (draw_x, draw_y))