from pygame import Vector2
import math
from configs import config
from models.collidable import CollisionBody
from models.game_state import GameState
from models.wall import Wall

# система AABB коллизии
class CollisionSystem:
    def __init__(self, state: GameState) -> None:
        self.impulses: dict[tuple[int, int], Vector2] = dict()
        self.collided_with_player = []
        self._state = state

    def resolve_obstacles(self, mover: CollisionBody, obstacles: list[Wall]) -> None:
        mover_rect = mover.rect
        for wall in obstacles:
            obs_rect = wall.rect
            if not mover_rect.colliderect(obs_rect):
                continue

            # вычисляем глубину пересечения по осям
            overlap_x = min(mover_rect.right - obs_rect.left, obs_rect.right - mover_rect.left)
            overlap_y = min(mover_rect.bottom - obs_rect.top, obs_rect.bottom - mover_rect.top)

            # ищем наименьшее пересечение
            if overlap_x < overlap_y:
                # горизонтальное столкновение
                if mover_rect.centerx < obs_rect.centerx:
                    mover_rect.right = obs_rect.left
                else:
                    mover_rect.left = obs_rect.right
                mover.ax = 0.0  # гасим скорость
                mover.vx = 0.0

            else:
                # вертикальное столкновение
                if mover_rect.centery < obs_rect.centery:
                    mover_rect.bottom = obs_rect.top
                else:
                    mover_rect.top = obs_rect.bottom
                mover.ay = 0.0  # аналогично гасим скорость
                mover.vy = 0.0


    def resolve_movers(self, movers: list[CollisionBody]) -> None:
        for i, _mover_1 in enumerate(movers):
            mover_1 = _mover_1.body
            if "terminal" in mover_1.tags:
                continue

            for _mover_2 in movers[i+1:]:
                mover_2 = _mover_2.body
                if "terminal" in mover_2.tags:
                    continue

                if "player" in mover_1.tags or "player" in mover_2.tags:
                    enemy = _mover_1 if "player" in mover_2.tags else _mover_2
                    if mover_1.rect.colliderect(mover_2.rect) and enemy not in self.collided_with_player:
                        self._state.player.on_enemy_collide(enemy)
                        self.collided_with_player.append(enemy)
                    elif not mover_1.rect.colliderect(mover_2.rect) and enemy in self.collided_with_player:
                        self.collided_with_player.remove(enemy)

                    if enemy not in self.collided_with_player:
                        # проверяем хитбоксы скиллов
                        if self._state.player.first_skill.hitbox.colliderect(enemy.rect):
                            self._state.player.first_skill.on_enemy_collide(enemy)
                            self.collided_with_player.append(enemy)
                        if self._state.player.second_skill.hitbox.colliderect(enemy.rect):
                            self._state.player.second_skill.on_enemy_collide(enemy)
                            self.collided_with_player.append(enemy)

                    if self._state.player.ignore_enemy:
                        continue

                rect_1 = mover_1.rect
                rect_2 = mover_2.rect

                if not rect_1.colliderect(rect_2):
                    self.impulses[(id(mover_1), id(mover_2))] = Vector2(0)
                    continue

                # вычисляем глубину пересечения по осям
                overlap_x = min(rect_1.right - rect_2.left, rect_2.right - rect_1.left)
                overlap_y = min(rect_1.bottom - rect_2.top, rect_2.bottom - rect_1.top)

                # ищем наименьшее пересечение
                if overlap_x < overlap_y:
                    # горизонтальное столкновение
                    if rect_1.centerx < rect_2.centerx:
                        rect_1.right, rect_2.left = rect_2.left, rect_1.right
                    else:
                        rect_1.left, rect_2.right = rect_2.right, rect_1.left
                    mover_1.vx = 0.0
                    mover_2.vx = 0.0
                else:
                    # вертикальное столкновение
                    if rect_1.centery < rect_2.centery:
                        rect_1.bottom, rect_2.top = rect_2.top, rect_1.bottom
                    else:
                        rect_1.top, rect_2.bottom = rect_2.bottom, rect_1.top
                    mover_1.vy = 0.0
                    mover_2.vy = 0.0


    def sub_step_moving(self, mover: CollisionBody, dt: float, vel: float) -> None:
        steps = max(1, math.ceil(vel * dt / (config.TILE_SIZE / 2)))
        sub_dt = dt / steps

        for _ in range(steps):
            # Применяем движение частями
            mover.rect.x += mover.vx * sub_dt
            mover.rect.y += mover.vy * sub_dt

            # Разрешаем коллизии на каждом подшаге
            self.resolve_obstacles(mover, self._state.room_manager.active_room.walls)
            if self._state.room_manager.active_room.terminal:
                self._state.collision_system.resolve_obstacles(mover,
                                                               [self._state.room_manager.active_room.terminal])