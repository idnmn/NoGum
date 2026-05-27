import random
import pygame
import config
from models.enemies import *


class Spawner:
    def __init__(self, state: GameState):
        self._state = state

    def _spawn_bookworm(self, x: float, y: float, level: float, state: GameState) -> BookWorm:
        size = int(random.uniform(30, 50))
        bookworm = BookWorm(
            x=x,
            y=y,
            size_x=size,
            size_y=int(size*0.75),
            level=level,
            sprite=self._state.assets['bookworm_sprite'],
            state=state
        )
        return bookworm

    def _spawn_bookworm_mommy(self, x: float, y: float, level: float, state: GameState) -> BookWormMommy:
        size = int(random.uniform(70, 90))
        mommy = BookWormMommy(
            x=x,
            y=y,
            size_x=size,
            size_y=int(size * 0.75),
            level=level,
            sprite=self._state.assets['bookworm_sprite'],
            state=state
        )
        return mommy

    def spawn_in_room(self, room: Room, state: GameState) -> list[Enemy]:
        enemies = []

        # разделяем мобов по "очкам спавна"
        score_1_enemy = [self._spawn_bookworm]
        score_2_enemy = [self._spawn_bookworm]
        score_3_enemy = [self._spawn_bookworm_mommy]

        # разбиваем spawn_score на слагаемые от 1 до 3 (система как в PvZ, где более сильные враги больше "весят")
        enemy_partition = self._random_partition(random.randint(state.spawn_score - 1, state.spawn_score + 1))

        # находим свободное пространство
        spaces = []
        layout = room.layout
        player_layout = Vector2(state.player.rect.center) // config.TILE_SIZE
        for i in range(1, len(layout) + 1):
            for j in range(1, len(layout[0]) + 1):
                if abs(i - player_layout.x) == 1 or abs(j - player_layout.y) == 1:
                    continue
                if layout[i - 1][j - 1] == '0':
                    spaces.append((j, i))

        offset = room.offset

        # заполняем пространство врагами
        for enemy_score in enemy_partition:
            x, y = Vector2(spaces.pop(random.randint(0, len(spaces) - 1))) * config.TILE_SIZE + offset

            if enemy_score == 1:
                enemies.append(random.choice(score_1_enemy)(x, y, config.LEVEL_COEF ** state.level_number, state))
            elif enemy_score == 2:
                enemies.append(random.choice(score_2_enemy)(x, y, config.LEVEL_COEF ** state.level_number, state))
            else:
                enemies.append(random.choice(score_3_enemy)(x, y, config.LEVEL_COEF ** state.level_number, state))
        return enemies

    def _random_partition(self, limit: int) -> list[int]:
        """
           случайно разбивает limit на сумму целых чисел из диапазона [min_val, max_val]
           возвращает список слагаемых сумма которых равна limit
        """
        min_val = 1
        max_val = 3
        k_min = math.ceil(limit / max_val)
        k_max = limit // min_val

        # случайное количество слагаемых
        k = random.randint(k_min, k_max)

        # преобразуем задачу: ищем k чисел в [0, M] с суммой S
        M = max_val - min_val
        S = limit - k * min_val

        result = []
        remaining = S

        for i in range(k - 1):
            # максимум, который можно взять сейчас
            max_possible = min(M, remaining)
            # минимум, который ОБЯЗАТЕЛЬНО нужно взять чтобы остальные части не превысили M
            min_possible = max(0, remaining - (k - 1 - i) * M)

            val = random.randint(min_possible, max_possible)
            result.append(val + min_val)
            remaining -= val

        # последнее слагаемое определяется однозначно
        result.append(remaining + min_val)
        return result

