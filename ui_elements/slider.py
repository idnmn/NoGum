import pygame
import config
from core import utils
from pygame import Vector2
from collections.abc import Callable
from models.game_state import GameState


class Slider():
    def __init__(self, title: str, x: float, y: float, width: float, max_value: float, min_value: float,
                 setter: Callable, stepped: bool = False, step: float = 0.0, round: int = 2,
                 default_value: float = 0.0, signature_color: tuple[int, int, int] = config.SLIDER_FILL_COLOR) -> None:
        self.interactive_hitbox = pygame.Rect(x, y - 5, width, 25)
        self.title = title
        self.x, self.y = x, y
        self.width = width
        self.height = 25
        self._font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 20)
        self.signature_color = signature_color

        self._value = default_value
        self.max_value = max_value
        self._min_value = min_value
        self._round = round

        self._stepped = stepped
        self._step = step

        self.setter = setter

    def change_position(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.interactive_hitbox = pygame.Rect(x, y - 5, self.width, 25)

    def render(self, surface: pygame.Surface) -> None:
        # подпись
        title_offset = 20 if not self._stepped else 25
        title = self._font.render(f"{self.title}: {self._value:.{self._round}f}",
                                  True, (220, 220, 220))
        surface.blit(title, (self.x, self.y - title_offset))

        # подложка
        pygame.draw.rect(surface, config.SLIDER_BACKGROUND_COLOR,
                         (self.x, self.y + 5, self.width, self.height - 10), border_radius=10)

        # заполнение
        fill_width = self.width * ((self._value - self._min_value) / (self.max_value - self._min_value))
        pygame.draw.rect(surface, self.signature_color,
                         (self.x, self.y + 5, fill_width, self.height - 10), border_radius=10)

        # насечки для ступенчатого слайдера
        if self._stepped:
            steps_count = int((self.max_value - self._min_value) / self._step)
            for i in range(1, steps_count + 1):
                gap_x = self.width // steps_count
                pygame.draw.line(surface, config.SLIDER_BACKGROUND_COLOR,
                                 (self.x + gap_x * i - i, self.y - 5),
                                 (self.x + gap_x * i - i, self.y), width=2)

                pygame.draw.line(surface, config.SLIDER_BACKGROUND_COLOR,
                                 (self.x + gap_x * i - i, self.y + 5),
                                 (self.x + gap_x * i - i, self.y + 19), width=2)


        # ползунок
        knob_rect_outside = (self.x + fill_width - 10, self.y, 20, 25)
        knob_rect_inside = (self.x + fill_width - 8, self.y + 2, 16, 21)
        pygame.draw.rect(surface, config.SLIDE_KNOB_OUTSIDE_COLOR, knob_rect_outside, border_radius=3)
        pygame.draw.rect(surface, config.SLIDE_KNOB_INSIDE_COLOR, knob_rect_inside, border_radius=3)

    def handle_click(self, mouse_pos):
        new_value = self._min_value + (self.max_value - self._min_value) * (mouse_pos[0] - self.x) / self.width

        self.value = new_value

        self.setter(self.value)

    def update(self, dt: float, mouse_pos: Vector2, _: GameState) -> None:
        pass

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value):
        # слайдер с фиксированными шагами
        if self._stepped:
            steps_to_value_l = (new_value - self._min_value) // self._step
            steps_to_value_h = (new_value - self._min_value) // self._step + 1

            stepped_value_l = self._min_value + self._step * steps_to_value_l
            stepped_value_h = self._min_value + self._step * steps_to_value_h

            if new_value - stepped_value_l < stepped_value_h - new_value:
                new_value = stepped_value_l
            else:
                new_value = stepped_value_h

        self._value = new_value
        if self._value > self.max_value:
            self._value = self.max_value

        if self._value < self._min_value:
            self._value = self._min_value

