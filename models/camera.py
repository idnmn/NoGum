import pygame
import config
import random

# класс камеры
class Camera:
    def __init__(self) -> None:
        self.position: pygame.Vector2 = pygame.Vector2(0, 0)
        self.prev_center: pygame.Vector2 = pygame.Vector2(0, 0)
        self.curr_center: pygame.Vector2 = pygame.Vector2(0, 0)
        self.progress: float = 0.0
        self.is_transitioning: bool = False

        self.shake_amount: float = 0.0
        self.shake_timer: float = 0.0
        self.shake_offset: pygame.Vector2 = pygame.Vector2(0, 0)

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

        if self.shake_timer > 0:
            self.shake_timer -= dt
            if self.shake_timer <= 0:
                self.shake_offset = pygame.Vector2(0, 0)
            else:
                self.shake_offset.x = random.uniform(-self.shake_amount, self.shake_amount)
                self.shake_offset.y = random.uniform(-self.shake_amount, self.shake_amount)

    def start_transition(self, prev_center: tuple[float, float], curr_center: tuple[float, float]) -> None:
        self.prev_center = pygame.Vector2(prev_center)
        self.curr_center = pygame.Vector2(curr_center)
        self.position = self.prev_center.copy()
        self.progress = 0.0
        self.is_transitioning = True

        self.shake_offset = pygame.Vector2(0, 0)  # сброс тряски при смене комнаты

    # тряска камеры
    def shake(self, amount: float, duration: float) -> None:
        self.shake_amount = amount
        self.shake_timer = duration