import random
import pygame
import config
from models.game_state import GameState
from models.wall import Wall
from models.camera import Camera
from models.terminal import Terminal
from models.exit import Exit
from models.chest import Chest

class Room:
    def __init__(self, layout_path: str, offset_x: float, offset_y: float, depth: int,
                 connections: set[str] | None, wall_sprite: pygame.Surface, floor_sprite: pygame.Surface,
                 terminal_sprites: list[pygame.Surface], waves_count: int = 0) -> None:
        self.connections = connections or set()
        self.offset = pygame.Vector2(offset_x, offset_y)
        self.walls: list[Wall] = []
        self.doors: list[Wall] = []
        self.terminal: Terminal | None = None
        self.exit: Exit | None = None
        self.chest: Chest | None = None
        self.bounds = pygame.Rect(
            self.offset.x,
            self.offset.y,
            config.ROOM_COLS * config.TILE_SIZE,
            config.ROOM_ROWS * config.TILE_SIZE
        )

        self.is_explored = False
        self.is_closed = False
        self.waves_count = waves_count
        self.depth = depth
        self.layout = []

        self.wall_sprite = wall_sprite
        self.floor_sprite = floor_sprite
        self.floor_surface: pygame.Surface = pygame.Surface((1, 1))
        self.terminal_sprite_active = terminal_sprites[0]
        self.terminal_sprite_inactive = terminal_sprites[1]

        self.load_layout_from_txt(layout_path)

    # щагрузка лайаута из txt
    def load_layout_from_txt(self, path: str) -> None:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            print('fallback')
            lines = self._generate_fallback_layout()

        # рандомно зеркалим комнату по осям
        step_x = random.choice((-1, 1))
        step_y = random.choice((-1, 1))

        for i in range(len(lines)):
            lines[i] = lines[i][::step_x]

        lines = lines[::step_y]

        self.layout = lines

        self.load_layout_from_matrix(self.layout)

    # загрузка лайаута из матрицы
    def load_layout_from_matrix(self, layout: list[str]) -> None:
        self.walls = []
        self.layout = layout

        rows_count = len(layout)
        cols_count = max(len(line) for line in layout)

        # Вычисляем физические границы комнаты
        self.bounds = pygame.Rect(
            self.offset.x, self.offset.y,
            cols_count * config.TILE_SIZE, rows_count * config.TILE_SIZE
        )

        # ️ генерируем поверхность пола
        self._build_floor_surface(self.bounds.width, self.bounds.height, self.floor_sprite)

        # вычисляем индексы центральных тайлов для проходов
        mid_row = config.ROOM_ROWS // 2

        passage_rows = set(range(max(0, mid_row - 1), min(config.ROOM_ROWS, mid_row + 2)))

        mid_col = config.ROOM_COLS // 2
        passage_cols = set(range(max(0, mid_col - 2), min(config.ROOM_COLS, mid_col + 2)))

        for row_idx, line in enumerate(layout):
            for col_idx, char in enumerate(line):
                # добавляем стены
                if char == config.ROOM_SYMBOL_WALL:
                    # Проверяем, является ли текущая стена частью прохода
                    is_passage = (
                            (col_idx == 0 and row_idx in passage_rows and 'left' in self.connections) or
                            (col_idx == config.ROOM_COLS - 1 and row_idx in passage_rows and 'right' in self.connections) or
                            (row_idx == 0 and col_idx in passage_cols and 'top' in self.connections) or
                            (row_idx == config.ROOM_ROWS - 1 and col_idx in passage_cols and 'bottom' in self.connections)
                    )

                    x = self.offset.x + col_idx * config.TILE_SIZE
                    y = self.offset.y + row_idx * config.TILE_SIZE
                    if not is_passage:
                        pass
                        self.walls.append(Wall(x, y, config.TILE_SIZE, self.wall_sprite))
                    else:
                        self.doors.append(Wall(x, y, config.TILE_SIZE, self.wall_sprite))

                # добавляем терминал
                if char == config.ROOM_SYMBOL_TERMINAL:
                    x = self.offset.x + col_idx * config.TILE_SIZE
                    y = self.offset.y + row_idx * config.TILE_SIZE

                    self.terminal = Terminal(x, y, config.TILE_SIZE,
                                             self.terminal_sprite_active, self.terminal_sprite_inactive)

    # обновляет состояние комнаты (открыто/закрыто)
    def update_room_state(self, is_cleared: bool, camera: Camera, state: GameState) -> None:
        # вычисляем индексы центральных тайлов для проходов
        if not is_cleared and not self.is_closed:
            self.walls += self.doors
            self.is_closed = True
            state.audio_manager.play_sound('door_close', 1.2)

            if self.terminal:
                self.terminal.is_active = False

            camera.shake(10, 0.15)

        elif is_cleared and self.is_closed:
            for door in self.doors:
                self.walls.remove(door)
            self.is_closed = False

            if self.terminal:
                self.terminal.is_active = True

            camera.shake(10, 0.15)

        elif is_cleared and not self.is_closed:
            if self.terminal:
                self.terminal.is_active = True

    # создает поверхность пола из тайлов
    def _build_floor_surface(self, width: int, height: int, tile: pygame.Surface) -> None:
        tile_w, tile_h = tile.get_width(), tile.get_height()
        self.floor_surface = pygame.Surface((width, height + tile_h))

        # Заполняем поверхность тайлами
        for y in range(0, height + tile_h, tile_h):
            for x in range(0, width, tile_w):
                self.floor_surface.blit(tile, (x, y))

    # генерирует комнату 26x15 с стенами по периметру, если файл не найден
    def _generate_fallback_layout(self) -> list[str]:
        print('Room Fallback')
        rows = []
        for r in range(config.ROOM_ROWS):
            if r == 0 or r == config.ROOM_ROWS - 1:
                rows.append(config.ROOM_SYMBOL_WALL * config.ROOM_COLS)
            else:
                rows.append(config.ROOM_SYMBOL_WALL + config.ROOM_SYMBOL_EMPTY * (config.ROOM_COLS - 2) + config.ROOM_SYMBOL_WALL)
        return rows

    def contains_point(self, point: tuple[float, float]) -> bool:
        return self.bounds.collidepoint(point)