import random
import pygame
import os
import config
from collections import deque
from models.game_state import GameState
from models.room import Room
from models.exit import Exit


class LevelGenerator:
    def __init__(self, wall_sprite: pygame.Surface, floor_sprite: pygame.Surface,
                 exit_sprite: pygame.Surface, state: GameState, layout_pool: list[str] | None = None) -> None:
        if layout_pool:
            # если список передан вручную используем его
            self.layout_pool = layout_pool
        else:
            # сканируем папку лайаутов на наличие новых лайаутов
            self.layout_pool = []
            dir_path = config.LAYOUTS_DIR

            if os.path.exists(dir_path):
                for file_name in os.listdir(dir_path):
                    if file_name.endswith(".txt"):
                        self.layout_pool.append(os.path.join(dir_path, file_name))

            # Fallback: если папка пуста, пробуем хотя бы дефолтный файл
            if not self.layout_pool:
                fallback = os.path.join(config.LAYOUTS_DIR, "L0.txt")
                if os.path.exists(fallback):
                    self.layout_pool.append(fallback)
                else:
                    print("Пупупу, нет лайаутов")

        self._state = state

        self.rooms: list[Room] = []
        self.occupied: set[tuple[int, int]] = set()
        self.spacing_x = (config.ROOM_COLS - 1) * config.TILE_SIZE
        self.spacing_y = (config.ROOM_ROWS - 1) * config.TILE_SIZE

        self.wall_sprite = wall_sprite
        self.floor_sprite = floor_sprite
        self.exit_sprite = exit_sprite
        self.terminal_sprites = [state.assets['terminal_sprite_active'],
                                 state.assets['terminal_sprite_inactive']]

    def generate(self, start_col: int, start_row: int) -> (list[Room], Room):
        self.rooms.clear()
        self.occupied.clear()
        rooms_count = random.randint(config.MIN_ROOMS, config.MAX_ROOMS)

        # строим карту при помощи BFS (поиск в ширину, храни господь дискретную математику)
        grid_layout: dict[tuple[int, int], list[set[str] | int]] = {}
        grid_layout[(start_col, start_row)] = [set(), 0]
        self.occupied.add((start_col, start_row))

        frontier = deque([(start_col, start_row, 1)])

        while frontier and len(grid_layout) < rooms_count:
            col, row, depth = frontier.popleft()

            # находим свободных соседей
            valid_neighbors = []
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nc, nr = col + dx, row + dy
                if (nc, nr) not in self.occupied:
                    valid_neighbors.append((nc, nr))

            if not valid_neighbors:
                continue

            is_start = (col == start_col and row == start_row)
            available = len(valid_neighbors)

            # корректируем количество выходов под оставшийся лимит
            remaining = rooms_count - len(grid_layout)
            max_exits = min(4 if is_start else available, remaining)
            num_exits = random.randint(1, max_exits)

            random.shuffle(valid_neighbors)
            for nc, nr in valid_neighbors[:num_exits]:
                if len(grid_layout) >= config.MAX_ROOMS:
                    break

                # определяем направления соединения
                if nc > col:
                    d_old, d_new = 'right', 'left'
                elif nc < col:
                    d_old, d_new = 'left', 'right'
                elif nr > row:
                    d_old, d_new = 'bottom', 'top'
                else:
                    d_old, d_new = 'top', 'bottom'

                grid_layout.setdefault((col, row), [set(), 0])[0].add(d_old)
                grid_layout.setdefault((nc, nr), [set(), 0])[0].add(d_new)
                grid_layout.setdefault((nc, nr), [set(), 0])[1] = depth + 1

                self.occupied.add((nc, nr))
                frontier.append((nc, nr, depth + 1))


        # сдвигаем всю карту в положительную четверть
        cols = [c for c, r in grid_layout.keys()]
        rows = [r for c, r in grid_layout.keys()]
        min_col, min_row = min(cols), min(rows)

        # считаем офсеты
        shift_x = -min_col * self.spacing_x
        shift_y = -min_row * self.spacing_y

        start_room_ref: Room | None = None

        max_depth = max([content[-1] for content in grid_layout.values()])

        # создание объектов
        for (col, row), content in grid_layout.items():
            connections = content[0]
            depth = content[1]

            offset_x = col * self.spacing_x + shift_x
            offset_y = row * self.spacing_y + shift_y

            #  запоминаем стартовую комнату по исходным координатам
            if col == start_col and row == start_row:
                room = Room("room_layouts/L0.txt", offset_x, offset_y, depth, connections,
                            wall_sprite=self.wall_sprite, floor_sprite=self.floor_sprite,
                            terminal_sprites=self.terminal_sprites, waves_count=0)
                room.is_explored = True
                start_room_ref = room

                new_layout = self._generate_terminal(room.layout)
                room.load_layout_from_matrix(new_layout)
                room.terminal.is_active = True
            else:
                layout_path = random.choice(self.layout_pool)
                room = Room(layout_path, offset_x, offset_y, depth, connections,
                            wall_sprite=self.wall_sprite, floor_sprite=self.floor_sprite,
                            terminal_sprites=self.terminal_sprites, waves_count=random.randint(config.MIN_WAVES,
                                                                                               config.MAX_WAVES))

                # с n-м шансом генерируем терминал
                if random.randint(0, 100) <= config.TERMINAL_CHANCE * min(1, (room.depth / max_depth) ** 2):
                    new_layout = self._generate_terminal(room.layout)
                    room.load_layout_from_matrix(new_layout)

            self.rooms.append(room)

        # генерируем выход в одной из комнат с максимальной глубиной
        max_depth_rooms = [room for room in self.rooms if room.depth == max_depth]
        exit_room = random.choice(max_depth_rooms)
        exit_room.load_layout_from_txt("room_layouts/L0.txt")
        exit_room.waves_count = 0
        exit_room.terminal = None
        exit_room.exit = Exit(exit_room.offset.x + config.TILE_SIZE * 11.5,
                              exit_room.offset.y + config.TILE_SIZE * 5.5,
                              config.EXIT_SIZE, self.exit_sprite, self._state.assets['exit_arrow'])
        # exit_room.is_explored = True

        return self.rooms, start_room_ref

    def _generate_terminal(self, layout) -> list[str]:
        spaces = []
        new_layout = []

        # ищем потенциальные места спавна
        for y in range(1, len(layout) - 3):
            for x in range(2, len(layout[0]) - 2):
                if layout[y][x] == '0' and layout[y+1][x] == '0':
                    neighbors_cords = [
                        (-1, -1), (0, -1), (1, -1),
                        (-1, 0), (1, 1), (0, 1), (-1, 1)
                    ]
                    walls_count = 0

                    for dx, dy in neighbors_cords:
                        if layout[y+dy][x+dx] == '*':
                            walls_count += 1

                    if walls_count <= 4:
                        spaces.append((x, y))
        # выбираем случайную точку из возможных
        if spaces:
            space = random.choice(spaces)
            line = list(layout[space[1]])
            line[space[0]] = 'T'
            layout[space[1]] = ''.join(line)
        # заполняем новый лайаут
        for line in layout:
            new_layout.append(line)
        return new_layout






