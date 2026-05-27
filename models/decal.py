import pygame
from pygame import Vector2


class Decal():
    def __init__(self, pos: Vector2, size_x: int, size_y: int, sprite: pygame.Surface, lifetime: float = -1,
                 max_alpha: int = 255, angle: float = 0.0, fade_time: float = 0.0) -> None:
        self.x = pos.x
        self.y = pos.y
        self.size_x = size_x
        self.size_y = size_y
        self.rotation = angle

        self.max_alpha = max_alpha
        self.lifetime = lifetime
        self.fade_time = fade_time
        self.sprite = pygame.transform.scale(sprite, (size_x, size_y))
        self.sprite.set_alpha(max_alpha)

        self.life_timer = lifetime
        self._alpha = 1.0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.size_x / 2, self.y  - self.size_y / 2,
                           self.size_x, self.size_y)

    def update(self, dt: float):
        if self.lifetime != -1:
            self.life_timer -= dt

            if self.life_timer <= self.fade_time:
                self._alpha = self.life_timer / self.fade_time
                self.sprite.set_alpha(max(0, int(self.max_alpha * self._alpha)))


    def render(self, surface: pygame.Surface) -> None:
        rotated = pygame.transform.rotate(self.sprite, self.rotation)

        surface.blit(rotated, (self.x, self.y))
