import os

import pygame

import config
from models.room import Room
from models.player import Player

# класс некого "оркестратора комнат", для удобной работы с несколькими комнатами
class RoomManager:
    def __init__(self) -> None:
        self.rooms: list[Room] = []
        self.active_room: Room | None = None
        self.prev_active_room: Room | None = None
        self.world_bounds: pygame.Rect | None = None

        # перекрытие 1 тайл: шаг сетки = (ширина_комнаты - 1) * размер_тайла
        self._spacing_x = (config.ROOM_COLS - 1) * config.TILE_SIZE
        self._spacing_y = (config.ROOM_ROWS - 1) * config.TILE_SIZE

        # self._load_initial_rooms()

    # позже будет гернератор карты
    def _load_initial_rooms(self) -> None:
        layout_path = os.path.join(config.LAYOUTS_DIR, "L0.txt")
        self.rooms.append(Room(layout_path, offset_x=0.0, offset_y=0.0))
        self.active_room = self.rooms[0]
        self.prev_active_room = self.rooms[0]

    def _generate_grid(self, cols: int=3, rows: int=3) -> None:
        layout_path = os.path.join(config.LAYOUTS_DIR, "L0.txt")
        for r in range(rows):
            row_rooms = []
            for c in range(cols):
                offset_x = c * self._spacing_x
                offset_y = r * self._spacing_y
                row_rooms.append(Room(layout_path, offset_x, offset_y))
            self.rooms += (row_rooms)
        self.active_room = self.rooms[0]
        self.prev_active_room = self.rooms[0]

        self._count_world_bounds()

    # активная - та комната, в которой находится игрок (в угоду оптимизации)
    def update_active_room(self, player: Player) -> Room | None:
        px, py = player.body.center
        if self.active_room and self.active_room.contains_point((px, py)):
            return self.active_room

        # Поиск новой комнаты
        for room in self.rooms:
            if room.contains_point((px, py)):
                return room

        if self.active_room is None:
            return self.rooms[0]

        return None

    # границы мира
    def _count_world_bounds(self) -> None:
        max_x = 0
        max_y = 0

        for room in self.rooms:
            if room.bounds.center[0] > max_x:
                max_x = room.bounds.center[0]
            if room.bounds.center[1] > max_y:
                max_y = room.bounds.center[1]

        width = max_x + (config.ROOM_COLS * config.TILE_SIZE / 2)
        height = max_y + (config.ROOM_ROWS * config.TILE_SIZE / 2)

        self.world_bounds = pygame.Rect(0, 0, int(width), int(height))
