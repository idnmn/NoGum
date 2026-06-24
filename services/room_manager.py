import pygame
from pygame import Vector2

from configs import config
from models.game_state import GameState
from models.room import Room
from models.player import Player
from models.terminal import Terminal
from services.level_generator import LevelGenerator

# класс некого "оркестратора комнат", для удобной работы с несколькими комнатами
class RoomManager:
    def __init__(self, wall_sprite: pygame.Surface, floor_sprite: pygame.Surface,
                 exit_sprite: pygame.Surface, state: GameState) -> None:
        self._generator = LevelGenerator(wall_sprite=wall_sprite,
                                         floor_sprite=floor_sprite,
                                         exit_sprite=exit_sprite,
                                         state=state)
        self._state = state

        self.rooms: list[Room] = []
        self.active_room: Room | None = None
        self.terminals: list[Terminal] = []

        self.is_new_explored = False
        self.active_room: Room | None
        self.prev_active_room: Room | None
        self.world_bounds: pygame.Rect | None

        self.max_depth: int

        self.initialize_level()

        # перекрытие 1 тайл: шаг сетки = (ширина_комнаты - 1) * размер_тайла
        self._spacing_x = (config.ROOM_COLS - 1) * config.TILE_SIZE
        self._spacing_y = (config.ROOM_ROWS - 1) * config.TILE_SIZE

    def initialize_level(self):
        self.rooms.clear()
        self.terminals.clear()
        self.rooms, self.start_room = self._generator.generate(0, 0)
        self.terminals = [room.terminal for room in self.rooms if room.terminal]

        self.is_new_explored = False
        self.active_room = self.start_room
        self.prev_active_room = self.active_room
        self._count_world_bounds()

        self.max_depth = max([room.depth for room in self.rooms])

    def switch_room_sprites(self, wall_sprite: pygame.Surface, floor_sprite: pygame.Surface,
                            exit_sprite: pygame.Surface) -> None:
        self._generator.wall_sprite = wall_sprite
        self._generator.floor_sprite = floor_sprite
        self._generator.exit_sprite = exit_sprite

    def update_interactives(self, state: GameState, dt):
        terminal = self.active_room.terminal
        exit = self.active_room.exit
        chest = self.active_room.chest

        # меняем состояние терминала если роядом игрок
        if terminal:
            if terminal.is_active:
                if terminal.interactive_hitbox.colliderect(state.player.rect) and not terminal.is_near_player:
                    terminal.is_near_player = True

                elif not terminal.interactive_hitbox.colliderect(state.player.rect) and terminal.is_near_player:
                    terminal.is_near_player = False

        # аналогично для выхода
        if exit:
            if exit.interactive_hitbox.rect.colliderect(state.player.rect):
                exit.is_near_player = True
            else:
                exit.is_near_player = False

        # аналогично для сундуков
        if chest:
            if chest.is_closed:
                if chest.interactive_hitbox.rect.colliderect(state.player.rect) and not chest.is_near_player:
                    chest.is_near_player = True

                elif not chest.interactive_hitbox.rect.colliderect(state.player.rect) and chest.is_near_player:
                    chest.is_near_player = False

            chest.update(dt, state)

        # invis для стен
        offset = self.active_room.offset
        walls_buffer = set()
        for entity in self._state.enemy_system.enemies + [self._state.player]:
            ex, ey = entity.rect.center - offset
            for wall in self.active_room.walls:
                dist_to_entity = (Vector2(wall.rect.center) - Vector2(entity.rect.center)).magnitude()
                if wall.rect.y - offset.y >= ey and (
                        config.TILE_SIZE * 24 >= wall.rect.x - offset.x >= config.TILE_SIZE):
                    if wall in walls_buffer:
                        wall.invis_ratio = min(wall.invis_ratio, min(255.0, 70 + (dist_to_entity / 200) ** 2 * 255))
                    else:
                        wall.invis_ratio = min(255.0, 70 + (dist_to_entity / 200) ** 2 * 255)
                        walls_buffer.add(wall)

        for wall in self.active_room.walls:
            if wall not in walls_buffer:
                wall.invis_ratio = 255
        walls_buffer.clear()

    # активная - та комната, в которой находится игрок (в угоду оптимизации)
    def update_active_room(self, player: Player) -> Room | None:
        px, py = player.body.center
        if self.active_room and self.active_room.contains_point((px, py)):
            return self.active_room

        # Поиск новой комнаты
        for room in self.rooms:
            if room.contains_point((px, py)):
                if not room.is_explored:
                    room.is_explored = True
                    self.is_new_explored = True
                    self._state.stattracker.rooms_explored += 1
                # для отрисовки тени терминала
                if room.terminal:
                    room.terminal.body.have_shadow = False
                return room

        if self.active_room is None:
            return self.rooms[0]

        return None

    # границы мира
    def _count_world_bounds(self) -> pygame.Rect | None:
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
        return

