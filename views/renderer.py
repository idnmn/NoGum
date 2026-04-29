import pygame
import config
from models.game_state import GameState

# Отрисовщик
class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen

    def render(self, state: GameState) -> None:
        self._screen.fill(config.BACKGROUND_COLOR)
        self._draw_player(state)
        pygame.display.flip()

    def _draw_player(self, state: GameState) -> None:
        rect = pygame.Rect(
            int(state.player_pos_x - config.PLAYER_SIZE / 2),
            int(state.player_pos_y - config.PLAYER_SIZE / 2),
            config.PLAYER_SIZE,
            config.PLAYER_SIZE
        )
        pygame.draw.rect(self._screen, (255, 255, 255), rect)