import pygame
from models.collidable import CollisionBody

# местные телепорты
class Terminal():
    def __init__(self, x: float, y: float, size: int,
                 sprite_active: pygame.Surface, sprite_inactive: pygame.Surface) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, size, size),
            layer="static",
            tags={"terminal"}
        )
        self.body.shadow_offset = -7

        self.interactive_hitbox = pygame.Rect(x - size, y - size, size * 3, size * 3)

        self.sprite_active = sprite_active.copy().convert_alpha()
        self.near_player_sprite = sprite_active.copy()
        self.near_player_sprite.fill((0, 30, 0, 0), None, pygame.BLEND_RGB_ADD)
        self.sprite_inactive = sprite_inactive.copy().convert_alpha()
        self.visual_offset_y = -(sprite_active.get_height() - size)

        self.is_active = False
        self.is_selected = False
        self.is_near_player = False

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def render(self, surface: pygame.Surface) -> None:
        draw_x = self.rect.x
        draw_y = self.rect.y + self.visual_offset_y

        # меняем спрайт если роядом игрок
        if self.is_active:
            if self.is_near_player:
                near_player_sprite = self.sprite_active.copy()
                near_player_sprite.fill((0, 30, 0, 0), None, pygame.BLEND_RGB_ADD)


            elif not self.is_near_player:
                self.sprite_active = self.sprite_active.copy()

        # отрисовываем спрайт
        if self.is_active:
            if self.is_near_player:
                sprite = self.near_player_sprite
            else:
                sprite = self.sprite_active
        else:
            sprite = self.sprite_inactive
        surface.blit(sprite, (draw_x, draw_y))