import pygame
import config
from models.game_state import GameState
from models.room_manager import RoomManager


# рендерер
class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen
        # создаем холст - поверхность фиксированного размера
        self._internal_surface = pygame.Surface(
            (config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT)
        )

    def render(self, state: GameState, room_manager: RoomManager) -> None:
        # рисуем всю игру на нашем маленьком холсте
        self._internal_surface.fill(config.BACKGROUND_COLOR)
        if state.player:
            self._draw_player(state.player)
        if room_manager.active_room:
            self._draw_walls(room_manager.active_room.walls)

        # масштабируем холст под размер реального экрана
        scaled_surface = pygame.transform.scale(
            self._internal_surface,
            self._screen.get_size()
        )

        # выводим результат на реальный экран
        self._screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

    def _draw_player(self, player: "Player") -> None:
        pygame.draw.rect(self._internal_surface, (255, 255, 255), player.body.rect)

    def _draw_walls(self, walls: list) -> None:
        for wall in walls:
            pygame.draw.rect(self._internal_surface, (80, 80, 90), wall.body.rect)