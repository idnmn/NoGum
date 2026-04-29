import math
from dataclasses import dataclass

@dataclass
class Player:
    x: float = 640.0
    y: float = 360.0
    speed: float = 300.0

    def move(self, dx: float, dy: float, dt: float) -> None:
        if dx == 0.0 and dy == 0.0:
            return

        # Нормализация
        length = math.hypot(dx, dy)
        norm_dx = dx / length
        norm_dy = dy / length

        # Перемещение
        self.x += norm_dx * self.speed * dt
        self.y += norm_dy * self.speed * dt