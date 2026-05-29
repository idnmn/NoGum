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
        # self.sprite_active = sprite_active.copy().convert_alpha()
        # self.near_player_sprite = sprite_active.copy()
        # self.near_player_sprite.fill((0, 30, 0, 0), None, pygame.BLEND_RGB_ADD)
        # self.sprite_inactive = sprite_inactive.copy().convert_alpha()
        # self.visual_offset_y = -(sprite_active.get_height() - size)

        self.is_near_player = False

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def render(self, surface: pygame.Surface) -> None:
        # pygame.draw.rect(surface, (255, 0, 0), self.interactive_hitbox)
        # if not self.is_near_player:
        #     pygame.draw.rect(surface, (255, 100, 100), self.rect)
        # else:
        #     pygame.draw.rect(surface, (100, 255, 100), self.rect)

        surface.blit(self._sprite, (self.rect.x, self.rect.y))

        if self.is_near_player:
            surface.blit(self.arrow_sprite, (self.body.rect.x + self.body.rect.width / 2 - 24,
                                             self.body.rect.y - 30))
