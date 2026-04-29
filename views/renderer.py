import pygame
import config
from models.game_state import GameState

# Отрисовщик
class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        # Создаем холст - поверхность фиксированного размера
        self._internal_surface = pygame.Surface(
            (config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT)
        )

    def render(self, state: GameState) -> None:
        # Рисуем всю игру на нашем маленьком холсте
        self._internal_surface.fill(config.BACKGROUND_COLOR)
        self._draw_player(state.player)

        # Масштабируем холст под размер реального экрана
        # get_size() вернет размер монитора, если включен FULLSCREEN
        scaled_surface = pygame.transform.scale(
            self._internal_surface,
            self._screen.get_size()
        )

        # Выводим результат на реальный экран
        self._screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def _draw_player(self, player: "Player") -> None:
        rect = pygame.Rect(
            int(player.x - config.PLAYER_SIZE / 2),
            int(player.y - config.PLAYER_SIZE / 2),
            config.PLAYER_SIZE,
            config.PLAYER_SIZE
        )
        pygame.draw.rect(self._internal_surface, (255, 255, 255), rect)