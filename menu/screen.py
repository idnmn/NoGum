import pygame
from pygame import Vector2
from models.game_state import GameState


# общий класс экрана меню
class MenuScreen:
    def __init__(self, state: GameState) -> None:
        self._state = state

        self.ui_elements = []
        self._buttons = []
        self._sliders = []

        self._dragging_slider = None

    def update(self, dt: float, mouse_pos: Vector2, events: list[pygame.event.Event]) -> None:
        for element in self.ui_elements:
            element.update(dt, mouse_pos, self._state)

        self._handle_events(events)

    def render(self, screen: pygame.Surface) -> None:
        for element in self.ui_elements:
            element.render(screen)

    def _handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self._state.is_running = False

            # нажатия кнопок
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self._buttons:
                    if button.state == 'selected':
                        button.click()
                        break

                # Обработка слайдеров
                for slider in self._sliders:
                    if slider.interactive_hitbox.collidepoint(event.pos):
                        slider.handle_click(event.pos)
                        self._dragging_slider = slider
                        break

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._dragging_slider = None
            elif event.type == pygame.MOUSEMOTION and self._dragging_slider:
                self._dragging_slider.handle_click(event.pos)

            # вернуться
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._back()

    def _back(self) -> None:
        pass