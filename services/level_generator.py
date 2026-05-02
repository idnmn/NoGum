import random
import os
import config
from collections import deque
from models.room import Room


class LevelGenerator:
    def __init__(self, layout_pool: list[str] | None = None) -> None:
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


        self.rooms: list[Room] = []
        self.occupied: set[tuple[int, int]] = set()
        self.spacing_x = (config.ROOM_COLS - 1) * config.TILE_SIZE
        self.spacing_y = (config.ROOM_ROWS - 1) * config.TILE_SIZE

    def generate(self, start_col: int, start_row: int) -> list[Room]:
        self.rooms.clear()
        self.occupied.clear()

        # 1. ЭТАП TOPOLOGY: BFS строит граф связей с учётом лимита
        grid_layout: dict[tuple[int, int], set[str]] = {}
        grid_layout[(start_col, start_row)] = set()
        self.occupied.add((start_col, start_row))

        # deque обеспечивает O(1) извлечение, что критично для циклов генерации
        frontier = deque([(start_col, start_row)])

        while frontier and len(grid_layout) < config.MAX_ROOMS:
            col, row = frontier.popleft()

            # Находим свободных соседей
            valid_neighbors = []
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nc, nr = col + dx, row + dy
                if (nc, nr) not in self.occupied:
                    valid_neighbors.append((nc, nr))

            if not valid_neighbors:
                continue

            is_start = (col == start_col and row == start_row)
            available = len(valid_neighbors)

            # 🔒 Корректируем количество выходов под оставшийся лимит
            remaining = config.MAX_ROOMS - len(grid_layout)
            max_exits = min(4 if is_start else available, remaining)
            num_exits = random.randint(1, max_exits)

            random.shuffle(valid_neighbors)
            for nc, nr in valid_neighbors[:num_exits]:
                if len(grid_layout) >= config.MAX_ROOMS:
                    break

                # Определяем направления соединения
                if nc > col:
                    d_old, d_new = 'right', 'left'
                elif nc < col:
                    d_old, d_new = 'left', 'right'
                elif nr > row:
                    d_old, d_new = 'bottom', 'top'
                else:
                    d_old, d_new = 'top', 'bottom'

                grid_layout.setdefault((col, row), set()).add(d_old)
                grid_layout.setdefault((nc, nr), set()).add(d_new)

                self.occupied.add((nc, nr))
                frontier.append((nc, nr))

        # сдвигаем всю карту в положительную четверть
        cols = [c for c, r in grid_layout.keys()]
        rows = [r for c, r in grid_layout.keys()]
        min_col, min_row = min(cols), min(rows)

        # считаем офсеты
        shift_x = -min_col * self.spacing_x
        shift_y = -min_row * self.spacing_y

        start_room_ref: Room | None = None

        # создание объектов
        for (col, row), connections in grid_layout.items():
            offset_x = col * self.spacing_x + shift_x
            offset_y = row * self.spacing_y + shift_y
            layout_path = random.choice(self.layout_pool)
            room = Room(layout_path, offset_x, offset_y, connections)
            self.rooms.append(room)

            #  запоминаем стартовую комнату по исходным координатам
            if col == start_col and row == start_row:
                start_room_ref = room

        return self.rooms, start_room_ref