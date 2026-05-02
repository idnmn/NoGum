import os

import pygame

import config
from models.room import Room
from models.player import Player
from services.level_generator import LevelGenerator

# класс некого "оркестратора комнат", для удобной работы с несколькими комнатами
class RoomManager:
    def __init__(self) -> None:
        self._generator = LevelGenerator()
        self.rooms, self.start_room = self._generator.generate(0, 0)

        self.active_room: Room | None = self.start_room
        self.prev_active_room: Room | None = self.active_room
        self.world_bounds: pygame.Rect | None = None
        self._count_world_bounds()

        # перекрытие 1 тайл: шаг сетки = (ширина_комнаты - 1) * размер_тайла
        self._spacing_x = (config.ROOM_COLS - 1) * config.TILE_SIZE
        self._spacing_y = (config.ROOM_ROWS - 1) * config.TILE_SIZE

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
        if not self.rooms:
            return pygame.Rect(0, 0, 0, 0)

        min_x = min(r.offset.x for r in self.rooms)
        min_y = min(r.offset.y for r in self.rooms)
        max_right = max(r.offset.x + r.bounds.width for r in self.rooms)
        max_bottom = max(r.offset.y + r.bounds.height for r in self.rooms)

        self.world_bounds = pygame.Rect(
            int(min_x), int(min_y),
            int(max_right - min_x), int(max_bottom - min_y)
        )

    # регенерация мира
    def regenerate(self) -> None:
        self.rooms = self._generator.generate(0, 0)
        self.active_room = self.rooms[0] if self.rooms else None
        self.prev_active_room = self.active_room
        self.world_bounds = self._count_world_bounds()
