import pygame
from models.collidable import CollisionBody


# ТЫЫЫЫЫ НЕ ПРОЙДЕЕЕЕЕЕЕЕЕЕЕЕЕШЬ! (стена)
class Wall():
    def __init__(self, x: float, y: float, size: int, sprite: pygame.Surface) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, size, size),
            layer="static",
            tags={"wall"}
        )

        self.sprite = sprite
        self.visual_offset_y = -(sprite.get_height() - size)
        self.invis_ratio = 255

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def render(self, surface: pygame.Surface) -> None:
        draw_x = self.rect.x
        draw_y = self.rect.y + self.visual_offset_y

        # отрисовываем спрайт
        sprite = self.sprite.copy()
        sprite.fill((255, 255, 255, self.invis_ratio), None, pygame.BLEND_RGBA_MULT)
        surface.blit(sprite, (draw_x, draw_y))

        del sprite