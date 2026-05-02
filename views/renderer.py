import pygame
import config
from models.game_state import GameState
from models.room_manager import RoomManager
from models.camera import Camera


# рендерер
class Renderer:
    def __init__(self, screen: pygame.Surface, world_bounds: pygame.Rect) -> None:
        self._screen = screen
        self._world_bounds = world_bounds

        # поверхность, на которой рисуется весь мир в абсолютных координатах
        self._world_surface = pygame.Surface((world_bounds.width, world_bounds.height))

        # буфер для финального кадра перед масштабированием
        self._viewport_buffer = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))

    def render(self, state: GameState, room_manager: RoomManager, camera: Camera) -> None:
        # очищаем экран
        self._world_surface.fill(config.BACKGROUND_COLOR)

        # во время перехода камеры рисуем обе комнаты
        if camera.is_transitioning and room_manager.prev_active_room:
            self._draw_walls(room_manager.prev_active_room.walls)
        if room_manager.active_room:
            self._draw_walls(room_manager.active_room.walls)

        # отрисовываем игрока
        if state.player:
            self._draw_player(state.player)

        # вычисляем координаты вьюпорта
        view_x = int(camera.position.x - config.INTERNAL_WIDTH / 2)
        view_y = int(camera.position.y - config.INTERNAL_HEIGHT / 2)
        view_rect = pygame.Rect(view_x, view_y, config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT)

        view_rect.clamp_ip(self._world_bounds) # ограничиваем размерами мира

        visible_chunk = self._world_surface.subsurface(view_rect) # вырезаем видимый чанк

        # масштабируем под размер экрана
        scaled_view = pygame.transform.scale(visible_chunk, self._screen.get_size())


        # выводим на экран
        self._screen.blit(scaled_view, (0, 0))
        pygame.display.flip()


    def _draw_player(self, player: "Player") -> None:
        pygame.draw.rect(self._world_surface, (255, 255, 255), player.body.rect)

    def _draw_walls(self, walls: list) -> None:
        for wall in walls:
            pygame.draw.rect(self._world_surface, (80, 80, 90), wall.body.rect)