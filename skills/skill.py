import pygame
from pygame import Vector2

from models.game_state import GameState


# общий шаблон класса для способностей
class Skill():
    def __init__(self, state: GameState) -> None:
        self._state = state

        self.cool_down = 0.0
        self._timer = 0.0

        self.is_using = False
        self.is_ready = False

        # констранты для рендера индикатора
        self.indicator_background_color = (30, 30, 30)
        self.indicator_fill_color = (220, 220, 220)

    def update(self, dt: float) -> None:
        self._timer -= dt

        if self._timer <= 0 and self.is_using:
            self.ended()

        if self._timer <= 0 and not self.is_using and not self.is_ready:
            self.reload()

    def render(self, surface: pygame.Surface) -> None:
        pass

    def reload(self) -> None:
        self.is_ready = True

    def ended(self) -> None:
        self.is_using = False
        self.is_ready = False
        self._timer = self.cool_down

    def use(self, mouse_pos: Vector2) -> None:
        self.is_using = True

    @property
    def cooldown_ratio(self):
        return max(0.0, min(1.0, 1.0 - (self._timer / self.cool_down)))
