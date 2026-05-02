import pygame
import config
from dataclasses import dataclass

# класс камеры
class Camera:
    def __init__(self) -> None:
        self.position: pygame.Vector2 = pygame.Vector2(0, 0)
        self.prev_center: pygame.Vector2 = pygame.Vector2(0, 0)
        self.curr_center: pygame.Vector2 = pygame.Vector2(0, 0)
        self.progress: float = 0.0
        self.is_transitioning: bool = False

    def update(self, dt: float) -> None:
        if self.is_transitioning:
            self.progress += dt * config.CAMERA_LERP_SPEED
            if self.progress >= 1.0:
                self.progress = 1.0
                self.is_transitioning = False
                self.position = self.curr_center.copy()
            else:
                # ease-out cubic
                t = 1.0 - (1.0 - self.progress) ** 3
                self.position = self.prev_center.lerp(self.curr_center, t)

    def start_transition(self, prev_center: tuple[float, float], curr_center: tuple[float, float]) -> None:
        self.prev_center = pygame.Vector2(prev_center)
        self.curr_center = pygame.Vector2(curr_center)
        self.position = self.prev_center.copy()
        self.progress = 0.0
        self.is_transitioning = True