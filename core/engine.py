import pygame
import config
from models.game_state import GameState
from controllers.input_handler import InputHandler
from views.renderer import Renderer

# Основной движок
class GameEngine:
    def __init__(self) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.WINDOW_TITLE)

        self._clock = pygame.time.Clock()
        self._state = GameState()
        self._input = InputHandler(self._state)
        self._renderer = Renderer(self._screen)

    def run(self) -> None:
        while self._state.is_running:
            self._input.process_events()
            self._renderer.render(self._state)
            self._clock.tick(config.FPS)

        pygame.quit()