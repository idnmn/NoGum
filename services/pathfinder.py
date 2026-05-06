import pygame
import config
from typing import List
from pygame import Vector2
from models.room import Room


class Pathfinder():
    def __init__(self) -> None:
        self.path_points = []

    def search_path(self, enemy_pos: Vector2, player_pos: Vector2, room: Room) -> None:
        self.path_points = []
        layout = [list(line) for line in room.layout]
        offset = room.offset

        enemy_room_pos = enemy_pos - offset
        player_room_pos = player_pos - offset

        enemy_layout = enemy_room_pos // config.TILE_SIZE
        player_layout = player_room_pos // config.TILE_SIZE

        enemy_layout = Vector2(int(enemy_layout.x), int(enemy_layout.y))
        player_layout = Vector2(int(player_layout.x), int(player_layout.y))

        layout[int(player_layout.y)][int(player_layout.x)] = 'P'
        layout[int(enemy_layout.y)][int(enemy_layout.x)] = 'E'

        cells_list = []
        closed_set = set()
        cells_dict = {}

        # стартовая клетка
        start_cell = Cell(
            x=int(enemy_layout.x),
            y=int(enemy_layout.y),
            prev_x=int(enemy_layout.x),
            prev_y=int(enemy_layout.y),
            layout=layout,
            prev_weight=0,
            player_layout=player_layout
        )
        cells_list.append(start_cell)
        cells_dict[(start_cell.x, start_cell.y)] = start_cell

        # защита от бесконечного цикла
        iteration = 0
        max_iter = len(layout) * len(layout[0]) * 4

        # строим маршрут до клетки игрока
        while cells_list and iteration < max_iter:
            iteration += 1

            # сортируем по возрастанию
            cells_list.sort(key=lambda cell: cell.weight + cell.evr_appr)

            # фильтруем стены и уже посещённые
            cells_list = [cell for cell in cells_list
                          if cell.is_space and (cell.x, cell.y) not in closed_set]

            if not cells_list:
                break

            lower_cell = cells_list.pop(0)  # берём клетку с наименьшим
            closed_set.add((lower_cell.x, lower_cell.y))  # помечаем как обработанную

            # проверяем дошли ли до конечной
            if lower_cell.x == player_layout.x and lower_cell.y == player_layout.y:
                # реконструкция пути от цели к старту через cells_dict
                path = []
                current = lower_cell
                while not (current.x == enemy_layout.x and current.y == enemy_layout.y):
                    path.append(Vector2(current.x * config.TILE_SIZE + config.TILE_SIZE // 2,
                                        current.y * config.TILE_SIZE + config.TILE_SIZE // 2) + offset)
                    prev_key = (current.prev_x, current.prev_y)
                    if prev_key in cells_dict:
                        current = cells_dict[prev_key]
                    else:
                        break
                self.path_points = path[::-1]  # разворачиваем путь
                return

            # print(lower_cell)
            # for line in layout: print(''.join(line))

            # соседи
            neighbors_cords = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ]
            for dx, dy in neighbors_cords:
                nx, ny = lower_cell.x + dx, lower_cell.y + dy

                # проверка границ комнаты
                if not (0 <= nx < len(layout[0]) and 0 <= ny < len(layout)):
                    continue
                # проверка на стену
                if layout[ny][nx] == '*':
                    continue
                # проверка на уже посещённую клетку
                if (nx, ny) in closed_set:
                    continue

                # проверка на дубликат с лучшим весом
                new_g = lower_cell.weight + (14 if abs(dx) + abs(dy) == 2 else 10)
                existing = cells_dict.get((nx, ny))
                if existing and existing.weight <= new_g:
                    continue  # уже есть клетка с таким или лучшим g-score

                cell = Cell(
                    x=nx,
                    y=ny,
                    prev_x=lower_cell.x,
                    prev_y=lower_cell.y,
                    layout=layout,
                    prev_weight=lower_cell.weight,
                    player_layout=player_layout
                )
                cells_list.append(cell)
                cells_dict[(cell.x, cell.y)] = cell  # сохраняем для реконструкции маршрута

        # если путь не найден или превышен лимит итераций
        self.path_points = []


class Cell():
    def __init__(self, x: int, y: int, prev_x: int, prev_y: int, layout: List[List[str]], prev_weight: int,
                 player_layout: Vector2) -> None:
        self.x = x
        self.y = y
        self.prev_x = prev_x
        self.prev_y = prev_y
        self.weight = 0

        self.is_space = layout[y][x] != '*'

        if abs(x - prev_x) + abs(y - prev_y) == 2:
            self.weight = 14 + prev_weight
        elif abs(x - prev_x) + abs(y - prev_y) == 1:
            self.weight = 10 + prev_weight

        self.evr_appr = (abs(x - int(player_layout.x)) + abs(y - int(player_layout.y))) * 10

    def __repr__(self):
        return f'Cell({self.x}, {self.y})\tPrev({self.prev_x}, {self.prev_y})\nweight: {self.weight}\nAppr: {self.evr_appr}\nSum: {self.evr_appr + self.weight}\n'