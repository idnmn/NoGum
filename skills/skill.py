import pygame
from pygame import Vector2

from models.game_state import GameState


# общий шаблон класса для способностей
class Skill():
    def __init__(self, state: GameState) -> None:
        self._state = state

        self._cool_down = 0.0
        self.cool_down_coef = 1.0
        self._cooldown_timer = 0.0
        self._use_timer = 0.0

        self.charges_count = 1
        self.max_charges = 1

        self.is_using = False
        self.is_ready = True

        # констранты для рендера индикатора
        self.indicator_background_color = (30, 30, 30)
        self.indicator_fill_color = (220, 220, 220)

    def update(self, dt: float) -> None:
        self._cooldown_timer -= dt
        self._use_timer -= dt

        if self._use_timer <= 0 and self.is_using:
            self.ended()

        if self._cooldown_timer <= 0 and not self.is_using and self.charges_count < self.max_charges:
            self.charges_count += 1
            self.is_ready = True
            if self.max_charges != 1:
                self._state.audio_manager.play_sound('skill_get_charge')
                self._cooldown_timer = self._cool_down

            if self.charges_count == self.max_charges:
                self.reload()
            else:
                self._cooldown_timer = self.cool_down

    def render(self, surface: pygame.Surface) -> None:
        pass

    def reload(self) -> None:
        self._state.audio_manager.play_sound('skill_reloaded')

    def ended(self) -> None:
        self.is_using = False
        if self.charges_count == 0:
            self.is_ready = False
        if self._cooldown_timer <= 0:
            self._cooldown_timer = self.cool_down

    def use(self, mouse_pos: Vector2) -> None:
        self.is_using = True
        self.charges_count -= 1

    @property
    def cool_down(self) -> float:
        return self._cool_down * self.cool_down_coef

    @property
    def cooldown_ratio(self):
        return max(0.0, min(1.0, 1.0 - (self._cooldown_timer / (self.cool_down))))
