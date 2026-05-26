import pygame
import config
from models.game_state import GameState
from models.room_manager import RoomManager
from models.player import Player


class MinimapRenderer:
    def __init__(self, screen: pygame.Surface, state: GameState, room_manager: RoomManager) -> None:
        self._screen = screen
        self._surface = pygame.Surface((config.MINIMAP_WIDTH, config.MINIMAP_HEIGHT), pygame.SRCALPHA)

        # позиция по центру
        self._map_rect = pygame.Rect(
            int((screen.get_width()  - config.MINIMAP_WIDTH) / 2),
            int((screen.get_height()  - config.MINIMAP_HEIGHT) / 2),
            config.MINIMAP_WIDTH,
            config.MINIMAP_HEIGHT
        )

        # основной слой для финального вывода (с альфа-каналом)
        self._layer = pygame.Surface(self._map_rect.size, pygame.SRCALPHA)

        # кэш для статичных элементов (комнаты + стены). Не перерисовывается каждый кадр.
        self._static_cache: pygame.Surface | None = None

        self._scale: float = 1.0
        self._offset: tuple[float, float] = (0.0, 0.0)
        self._world_bounds: pygame.Rect = pygame.Rect(0, 0, 1, 1)

        self.initialize_room_data(room_manager, state)

        self._player = state.player

    def initialize_room_data(self, room_manager: RoomManager, state: GameState) -> None:
        self._room_manager = room_manager
        self._set_world_bounds(self._room_manager.world_bounds)
        self._walls_color = config.MINIMAP_WALL_COLOR_LIST[state.level_seed - 1]

    # сброс кэша
    def invalidate_cache(self) -> None:
        self._static_cache = None

    # вычисляет масштаб и смещение для центрирования уровня на карте
    def _set_world_bounds(self, bounds: pygame.Rect) -> None:
        self._world_bounds = bounds
        if bounds.width > 0 and bounds.height > 0:
            margin = 12
            self._scale = min(
                (self._map_rect.width - margin) / bounds.width,
                (self._map_rect.height - margin) / bounds.height
            )
            self._offset = (
                (self._map_rect.width - bounds.width * self._scale) / 2,
                (self._map_rect.height - bounds.height * self._scale) / 2
            )

    def render(self) -> None:
        # рендерим статичную часть только при открытии новых комнат или пустом кэшэ
        if self._room_manager.is_new_explored or self._static_cache is None:
            self._static_cache = pygame.Surface(self._map_rect.size, pygame.SRCALPHA)
            self._static_cache.fill((0, 0, 0, 0))
            self._draw_static(self._room_manager)
            self._room_manager.is_new_explored = False

        # очищаем динамический слой
        self._layer.fill((0, 0, 0, 0))

        # Подложка и рамка карты
        pygame.draw.rect(self._layer, config.MINIMAP_BG_COLOR, self._layer.get_rect(), border_radius=6)
        pygame.draw.rect(self._layer, config.MINIMAP_BORDER_COLOR, self._layer.get_rect(), 2, border_radius=6)

        # Накладываем кэш комнат и стен
        self._layer.blit(self._static_cache, (0, 0))

        # рисуем динамические элементы (игрок и PoI)
        self._draw_player(self._player)

        # выводим на экран
        self._screen.blit(self._layer, self._map_rect)
        # pygame.display.flip()

    # отрисовка полов и стен. Выполняется редко, кэшируется
    def _draw_static(self, room_manager: RoomManager) -> None:
        # Фоны комнат
        for room in room_manager.rooms:
            if room.is_explored or config.MINIMAP_EXPLORED:
                rx = self._offset[0] + (room.offset.x - self._world_bounds.x) * self._scale
                ry = self._offset[1] + (room.offset.y - self._world_bounds.y) * self._scale
                rw = room.bounds.width * self._scale
                rh = room.bounds.height * self._scale
                pygame.draw.rect(self._static_cache, config.MINIMAP_ROOM_BG_COLOR, (rx, ry, rw, rh))

                # стены (каждый тайл рисуется отдельно)
                for wall in room.walls:
                    self._draw_object(wall.body.rect, self._walls_color)

                if room.terminal:
                    terminal = room.terminal
                    if terminal.is_active:
                        color = config.TERMINAL_ACTIVE_COLOR
                    else:
                        color = config.TERMINAL_INACTIVE_COLOR

                    self._draw_object(terminal.body.rect, color, 2.0)

                if room.exit:
                    exit = room.exit

                    self._draw_object(exit.body.rect, config.EXIT_COLOR)

    def _draw_object(self, obj_rect: pygame.Rect, color: tuple[int, int, int], size_coef: float = 1.0) -> None:
        mw = obj_rect.width * self._scale * size_coef
        mh = obj_rect.height * self._scale * size_coef

        if size_coef != 1:
            size_offset_x = mw / 2
            size_offset_y = mh / 2
        else:
            size_offset_x = 0
            size_offset_y = 0

        mx = self._offset[0] + (obj_rect.x - self._world_bounds.x) * self._scale - size_offset_x
        my = self._offset[1] + (obj_rect.y - self._world_bounds.y) * self._scale - size_offset_y
        pygame.draw.rect(self._static_cache, color, (mx, my, mw, mh))

    # отрисовка игрока
    def _draw_player(self, player: Player) -> None:
        px = self._offset[0] + (player.body.center[0] - self._world_bounds.x) * self._scale
        py = self._offset[1] + (player.body.center[1] - self._world_bounds.y) * self._scale

        # размер маркера адаптируется под масштаб карты
        radius = max(3, int(self._scale * 8))
        pygame.draw.circle(self._layer, config.MINIMAP_PLAYER_COLOR, (int(px), int(py)), radius)