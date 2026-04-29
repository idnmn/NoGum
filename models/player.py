import math
from dataclasses import dataclass

@dataclass
class Player:
    x: float = 640.0
    y: float = 360.0
    vx: float = 0.0
    vy: float = 0.0

    # Cостояние рывка
    _dash_timer: float = 0.0
    _dash_cooldown_timer: float = 0.0

    def update(self, dx: float, dy: float, dt: float,
               acceleration: float, friction: float, max_speed: float,
               dash_speed: float, dash_duration: float, dash_cooldown: float,
               dash_requested: bool) -> None:
        """
        dx, dy: Направление ввода
        dt: Delta time в секундах
        acceleration, friction, max_speed: ускорение, трение и макс. скорость
        dash_... - параметры рывка (длительность, скорость, кд и флаг отработки)
        """

        # Обновляем таймер для кд
        if self._dash_cooldown_timer > 0:
            self._dash_cooldown_timer -= dt

        # Делаем рывок (коли можем)
        if dash_requested and self._dash_cooldown_timer <= 0 and (dx != 0 or dy != 0):
            self._dash_timer = dash_duration
            self._dash_cooldown_timer = dash_cooldown
        # Обновляем таймер для рывка
        if self._dash_timer > 0:
            self._dash_timer -= dt

        # Используем параметры рывка, пока активен его таймер
        current_max_speed = dash_speed if self._dash_timer > 0 else max_speed
        current_accel = acceleration * 10 if self._dash_timer > 0 else acceleration

        # Вычисляем ускорение из ввода
        if dx != 0.0 or dy != 0.0:
            length = math.hypot(dx, dy)
            ax = (dx / length) * current_accel
            ay = (dy / length) * current_accel
        else:
            ax = ay = 0.0
            # Применяем трение
            damping = math.exp(-friction * dt)
            self.vx *= damping
            self.vy *= damping

        # Интегрируем ускорение в скорость
        self.vx += ax * dt
        self.vy += ay * dt

        # Ограничиваем максимальную скорость
        current_speed = math.hypot(self.vx, self.vy)
        if current_speed > max_speed:
            scale = current_max_speed / current_speed
            self.vx *= scale
            self.vy *= scale

        # Защита от дрейфа
        if current_speed < 2.0:
            self.vx = 0.0
            self.vy = 0.0

        # Обновляем позицию
        self.x += self.vx * dt
        self.y += self.vy * dt