import os
import config
from models.room import Room
from models.player import Player

# класс некого "оркестратора комнат", для удобной работы с несколькими комнатами
class RoomManager:
    def __init__(self) -> None:
        self.rooms: list[Room] = []
        self.active_room: Room | None = None
        self._load_initial_rooms()

    # позже будет гернератор карты
    def _load_initial_rooms(self) -> None:
        layout_path = os.path.join(config.LAYOUTS_DIR, "L0.txt")
        self.rooms.append(Room(layout_path, offset_x=0.0, offset_y=0.0))
        self.active_room = self.rooms[0]

    # активная - та комната, в которой находится игрок (в угоду оптимизации)
    def update_active_room(self, player: Player) -> None:
        px, py = player.body.center
        if self.active_room and self.active_room.contains_point((px, py)):
            return

        # Поиск новой комнаты
        for room in self.rooms:
            if room.contains_point((px, py)):
                self.active_room = room
                return

        # если игрок застрял между комнатами
        if self.active_room is None and self.rooms:
            self.active_room = self.rooms[0]