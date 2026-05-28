import pygame
import config


class Slider():
    def __init__(self, title: str, x: float, y: float, width: float, max_value: float, min_value: float,
                 stepped: bool = False, step: float = 0.0, round: int = 2) -> None:
        self.interactive_hitbox = pygame.Rect(x, y - 5, width, 25)
        self.title = title
        self.x, self.y = x, y
        self.width = width
        self.height = 25
        self._font = pygame.font.Font("assets/QBF_font.ttf", 20)

        self.value = 0.0
        self._max_value = max_value
        self._min_value = min_value
        self._round = round

        self._stepped = stepped
        self._step = step

    def render(self, surface: pygame.Surface) -> None:
        # подпись
        title = self._font.render(f"{self.title}: {self.value:.{self._round}f}",
                                  True, (220, 220, 220))
        surface.blit(title, (self.x, self.y - 20))

        # подложка
        pygame.draw.rect(surface, config.SLIDER_BACKGROUND_COLOR,
                         (self.x, self.y + 5, self.width, self.height - 10), border_radius=10)

        # заполнение
        fill_width = self.width * ((self.value - self._min_value) / (self._max_value - self._min_value))
        pygame.draw.rect(surface, config.SLIDER_FILL_COLOR,
                         (self.x, self.y + 5, fill_width, self.height - 10), border_radius=10)

        # ползунок
        knob_rect_outside = (self.x + fill_width - 10, self.y, 20, 25)
        knob_rect_inside = (self.x + fill_width - 8, self.y + 2, 16, 21)
        pygame.draw.rect(surface, config.SLIDE_KNOB_OUTSIDE_COLOR, knob_rect_outside, border_radius=3)
        pygame.draw.rect(surface, config.SLIDE_KNOB_INSIDE_COLOR, knob_rect_inside, border_radius=3)

    def handle_click(self, mouse_pos):
        new_value = (self._max_value - self._min_value) * (mouse_pos[0] - self.x) / self.width

        self.value = new_value
        if self.value > self._max_value:
            self.value = self._max_value

        if self.value < self._min_value:
            self.value = self._min_value

