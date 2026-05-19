import random
from xml.dom.minidom import Entity

import pygame
import math
from pygame import Vector2
import config
from models.collidable import CollisionBody
from models.decal import Decal
from models.room import Room
from models.game_state import GameState
from models.renderable import Renderable
from services.decal_system import DecalSystem
from services.pathfinder import Pathfinder


class Enemy(Renderable):
    def __init__(self, x: float, y: float, size_x: int, size_y: int, enemy_type: str = "") -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x - size_x / 2, y - size_y / 2, size_x, size_y),
            layer="dynamic",
            tags={"enemy", enemy_type}
        )

        self.attack_hitbox = pygame.Rect(
                self.body.rect.x - 1,
                self.body.rect.y - 1,
                self.body.rect.width + 2,
                self.body.rect.height + 2
            )

        self.type = enemy_type
        self.hp = 0.0
        self.defence = 0.0
        self.max_speed = 0.0
        self.attack_damage = 0.0
        self.attack_range = 0.0
        self._state_timer = 0.0
        self.state: str = ''
        self.is_alive = True
        self.impact_color = (255, 255, 255)

        self.pathfinder = Pathfinder()
        self._repath_cooldown = 0.0
        self._repath_timer = 0.0

        self.damage_cooldown = 0.5
        self._damage_timer = 0.0

        self.step_cooldown = 0.0
        self._step_timer = 0.0

        self._visual_damage_cooldown = 0.1
        self._visual_damage_timer = -1.0

        self._facing_right = True

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def update(self, dt: float, state: GameState, active_room: Room, surface: pygame.Surface) -> None:
        pass

    def update_timers(self, dt: float, surface: pygame.surface, active_room: Room, state: GameState) -> None:
        if self._repath_timer > 0:
            self._repath_timer -= dt

        if self._state_timer > 0:
            self._state_timer -= dt

        if self._damage_timer > 0:
            self._damage_timer -= dt

        if self._step_timer > 0:
            self._step_timer -= dt

        if self._visual_damage_timer > 0:
            self._visual_damage_timer -= dt

    def take_damage(self, amount: float) -> bool:
        damage = max(0, amount - self.defence)
        self.hp -= damage
        if self.hp <= 0:
            self.is_alive = False

        if damage > 0:
            self._visual_damage_timer = self._visual_damage_cooldown

        return damage

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 255, 255), self.body.rect)

class BookWorm(Enemy):
    def __init__(self, x: float, y: float, size_x: int, size_y: int, sprite: pygame.Surface,
                 enemy_type: str = "bookworm", level: float = 1.0) -> None:
        super().__init__(x, y, size_x, size_y, enemy_type)
        self._source_sprite = pygame.transform.scale(sprite, (size_x, size_y)).convert_alpha()
        self.sprite = self._source_sprite
        self.body.shadow_offset = -5

        # определяем статы
        self.hp = 20 * level
        self.max_hp = 20 * level
        self.max_speed = 500
        self.defence = 0.0
        self.dash_speed = 2000
        self.attack_damage = 20 * level * 0.5
        self.contact_damage = 25 * level * 0.2
        self.attack_range = 200
        self.aggr_range = 1000
        self.impact_color = (200, 0, 0)

        self.state: str = 'recovery'  # chase, charge, dash, recovery
        self._state_timer = 0.5
        self.dash_dir = Vector2(0)
        self.pre_attack_cooldown = 0.5              # кд перед рывком
        self.post_attack_cooldown = 0.2             # кд после рывка
        self.between_dash_cooldown = 2.0 / level    # кд между рывками
        self.dash_duration = 0.2                    # длительность рывка

        self.acceleration = 2500
        self.friction = config.FRICTION * 10
        self.next_point = Vector2(self.rect.center)

        self._repath_cooldown = 0.5

    def render(self, surface: pygame.Surface) -> None:
        # цветовая индикация состояния
        if self.state == "charge":
            color = (2, 0, 0, 0)  # Подготовка
            self.sprite.fill(color, None, pygame.BLEND_RGB_ADD)
        else:
            self.sprite = self._source_sprite.copy()

        # получение урона
        if self._visual_damage_timer > 0:
            self.sprite.fill((255, 0, 0, 0), None, pygame.BLEND_RGBA_ADD)

        # зеркалирование
        if self.body.vx < 0 and self._facing_right:
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self._source_sprite = pygame.transform.flip(self._source_sprite, True, False)
            self._facing_right = False
        elif self.body.vx > 0 and not self._facing_right:
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self._source_sprite = pygame.transform.flip(self._source_sprite, True, False)
            self._facing_right = True

        surface.blit(self.sprite, (self.rect.x, self.rect.y))

    def update(self, dt: float, state: GameState, active_room: Room, surface: pygame.Surface) -> None:
        # обновляем таймеры
        self.update_timers(dt, surface, active_room, state)

        # если ещё остались точки
        if self.pathfinder.path_points:
            distance = Vector2(self.body.rect.center).distance_to(Vector2(self.next_point))
            if distance <= config.TILE_SIZE - 5 and len(self.pathfinder.path_points) > 1:
                self.next_point = Vector2(self.pathfinder.path_points.pop(0))
                pygame.draw.circle(surface, (32, 255, 28), self.next_point - active_room.offset, 7)
        else:
            self.next_point = Vector2(self.body.rect.center)

        # Вектор и дистанция до игрока
        dist_to_player = Vector2(self.rect.center).distance_to(state.player.rect.center)
        dir_to_player = (pygame.Vector2(state.player.rect.center) - pygame.Vector2(self.rect.center)).normalize()

        # Обрабатываем логику по состояниям
        if self.state == 'chase':  # поиск игрока
            dx = self.next_point.x - self.body.rect.centerx
            dy = self.next_point.y - self.body.rect.centery

            # обновляем данные с pathfinder'а
            if self._repath_timer <= 0:
                self._repath_timer = self._repath_cooldown
                self.pathfinder.search_path(Vector2(self.rect.center), Vector2(state.player.rect.center), active_room,
                                            search_index=2)
                if self.pathfinder.path_points:
                    self.next_point = self.pathfinder.path_points[0]

                # debug рендер
                for i, point in enumerate(self.pathfinder.path_points):
                    draw_point = point - active_room.offset
                    pygame.draw.circle(surface, (255, 210, 80), (draw_point.x, draw_point.y), 5)

                    if i == 0:
                        pygame.draw.circle(surface, (255, 210, 80), self.rect.center - active_room.offset, 5)
                        pygame.draw.line(surface, (255, 210, 80), (draw_point.x, draw_point.y),
                                         self.rect.center - active_room.offset, 3)

                    if i + 1 < len(self.pathfinder.path_points):
                        next_draw = self.pathfinder.path_points[i + 1] - active_room.offset
                        pygame.draw.line(surface, (255, 210, 80), (draw_point.x, draw_point.y),
                                         (next_draw.x, next_draw.y), 3)

            # если игрок в радиусе атаки начинаем заряжать рывок
            if dist_to_player < self.attack_range and self._state_timer <= 0:
                self.state = "charge"
                self._state_timer = self.pre_attack_cooldown
                self.body.vx = 0.0
                self.body.vy = 0.0
                self.dash_dir = dir_to_player.copy()
            else:
                direction = Vector2(dx, dy)

                if direction.magnitude() < self.aggr_range and direction.magnitude() != 0:
                    direction = direction.normalize()
                    dx, dy = direction
                else:
                    direction = Vector2(0)
                    dx, dy = direction

                # вычисляем ускорение из pathfinder'а
                if dx != 0.0 or dy != 0.0:
                    ax = dx * self.acceleration
                    ay = dy * self.acceleration
                else:
                    ax = ay = 0.0
                    # применяем трение
                    damping = math.exp(-self.friction * dt)
                    self.body.vx *= damping
                    self.body.vy *= damping

                # интегрируем ускорение в скорость
                self.body.vx += ax * dt
                self.body.vy += ay * dt

                # ограничиваем максимальную скорость
                current_speed = self.body.velocity.magnitude()
                if current_speed > self.max_speed:
                    scale = self.max_speed / current_speed
                    self.body.vx *= scale
                    self.body.vy *= scale

                # защита от дрейфа
                if current_speed < 2.0:
                    self.body.vx = 0.0
                    self.body.vy = 0.0

        elif self.state == 'charge':  # готовится к рывку
            self.body.vx = 0.0
            self.body.vy = 0.0
            self.dash_dir = dir_to_player.copy()
            # делаем рывок
            if self._state_timer <= 0:
                self.state = "dash"
                self._state_timer = self.dash_duration
                self.body.vx = self.dash_dir.x * self.dash_speed
                self.body.vy = self.dash_dir.y * self.dash_speed

        elif self.state == "dash":
            # сбрасываем рывок при контакте или по истечению таймера
            if self.attack_hitbox.colliderect(state.player.rect) or self._state_timer <= 0:
                if self.attack_hitbox.colliderect(state.player.rect):
                    state.player.take_damage(self.attack_damage)
                    self._damage_timer = self.damage_cooldown

                self.state = "recovery"
                self._state_timer = self.post_attack_cooldown
                self.body.vx = 0.0
                self.body.vy = 0.0

        elif self.state == "recovery":
            if self._state_timer <= 0:
                self.state = "chase"
                self._state_timer = self.between_dash_cooldown

        # контактный урон
        if self.attack_hitbox.colliderect(state.player.rect) and self.state == "chase":
            if self._damage_timer <= 0:
                state.player.take_damage(self.contact_damage)
                self._damage_timer = self.damage_cooldown

        # обновляем позицию
        self.body.rect.x += self.body.vx * dt
        self.body.rect.y += self.body.vy * dt

        self.attack_hitbox.x = self.body.rect.x - 1
        self.attack_hitbox.y = self.body.rect.y - 1

    def on_death(self, state: GameState) -> None:
        random_size = random.randint(-3, 5)
        decal = Decal(
            pos=Vector2(self.body.rect.center),
            lifetime=15,
            size_x=self.body.rect.width + random_size,
            size_y=self.body.rect.width + random_size,
            angle= random.uniform(0, 360),
            sprite=state.assets['hit_decal'],
            fade_time=1,
            max_alpha=150,
        )

        state.decals_system.decals.append(decal)

class BookWormMommy(Enemy):
    def __init__(self, x: float, y: float, size_x: int, size_y: int, sprite: pygame.Surface,
                 enemy_type: str = "bookworm", level: float = 1.0) -> None:
        super().__init__(x, y, size_x, size_y, enemy_type)
        self._source_sprite = pygame.transform.scale(sprite, (size_x, size_y)).convert_alpha()
        self.sprite = self._source_sprite
        self.body.shadow_offset = -10

        # определяем статы
        self.hp = 50 * level
        self.max_hp = 50 * level
        self.max_speed = 300
        self.defence = 2.0
        self.dash_speed = 1000
        self.attack_damage = 25 * level * 0.5
        self.contact_damage = 25 * level * 0.2
        self.attack_range = 200
        self.aggr_range = 1000
        self.impact_color = (200, 0, 0)

        self.state: str = 'recovery'  # chase, charge, dash, recovery, death
        self._state_timer = 0.5
        self.dash_dir = Vector2(0)
        self.pre_attack_cooldown = 0.5              # кд перед рывком
        self.post_attack_cooldown = 0.5             # кд после рывка
        self.between_dash_cooldown = 3.0 / level    # кд между рывками
        self.dash_duration = 0.4                    # длительность рывка
        self.death_duration = 1.5

        self.acceleration = 2500
        self.friction = config.FRICTION * 10
        self.next_point = Vector2(self.rect.center)

        self._visual_damage_cooldown = 0.2
        self._visual_damage_timer = -1.0

        self._repath_cooldown = 0.5

        self._shake_amount = 0.0

    def render(self, surface: pygame.Surface) -> None:
        # зеркалирование
        if self.body.vx < 0 and self._facing_right:
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self._source_sprite = pygame.transform.flip(self._source_sprite, True, False)
            self._facing_right = False
        elif self.body.vx > 0 and not self._facing_right:
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self._source_sprite = pygame.transform.flip(self._source_sprite, True, False)
            self._facing_right = True

        sprite = self.sprite.copy()
        max_offset = 10 * self._shake_amount
        offset_x = random.uniform(-max_offset, max_offset)
        offset_y = random.uniform(-max_offset, max_offset)

        # цветовая индикация состояния
        if self.state == "charge":
            red = min(255, int(255 * (1 - (self._state_timer / self.pre_attack_cooldown)) ** 2))
            color = (red, 0, 0, 0)  # подготовка
            sprite.fill(color, None, pygame.BLEND_RGB_ADD)
        elif self.state == "death":
            color = (min(255, int(255 * self._shake_amount ** 2)), 0, 0, 0)  # смэрть
            sprite.fill(color, None, pygame.BLEND_RGB_ADD)
        else:
            sprite = self._source_sprite.copy()

        # получение урона
        if self._visual_damage_timer > 0 and self.state != 'death':
            sprite.fill((255, 0, 0, 0), None, pygame.BLEND_RGBA_ADD)


        surface.blit(sprite, (self.rect.x + offset_x, self.rect.y + offset_y))

    def update(self, dt: float, state: GameState, active_room: Room, surface: pygame.Surface) -> None:
        # обновляем таймеры
        self.update_timers(dt, surface, active_room, state)

        # если ещё остались точки
        if self.pathfinder.path_points:
            distance = Vector2(self.body.rect.center).distance_to(Vector2(self.next_point))
            if distance <= config.TILE_SIZE - 5 and len(self.pathfinder.path_points) > 1:
                self.next_point = Vector2(self.pathfinder.path_points.pop(0))
                pygame.draw.circle(surface, (32, 255, 28), self.next_point - active_room.offset, 7)
        else:
            self.next_point = Vector2(self.body.rect.center)

        # Вектор и дистанция до игрока
        dist_to_player = Vector2(self.rect.center).distance_to(state.player.rect.center)
        dir_to_player = (pygame.Vector2(state.player.rect.center) - pygame.Vector2(self.rect.center)).normalize()

        # Обрабатываем логику по состояниям
        if self.state == 'chase':  # поиск игрока
            dx = self.next_point.x - self.body.rect.centerx
            dy = self.next_point.y - self.body.rect.centery

            # обновляем данные с pathfinder'а
            if self._repath_timer <= 0:
                self._repath_timer = self._repath_cooldown
                self.pathfinder.search_path(Vector2(self.rect.center), Vector2(state.player.rect.center), active_room,
                                            search_index=0)
                if self.pathfinder.path_points:
                    self.next_point = self.pathfinder.path_points[0]

                # debug рендер
                for i, point in enumerate(self.pathfinder.path_points):
                    draw_point = point - active_room.offset
                    pygame.draw.circle(surface, (255, 210, 80), (draw_point.x, draw_point.y), 5)

                    if i == 0:
                        pygame.draw.circle(surface, (255, 210, 80), self.rect.center - active_room.offset, 5)
                        pygame.draw.line(surface, (255, 210, 80), (draw_point.x, draw_point.y),
                                         self.rect.center - active_room.offset, 3)

                    if i + 1 < len(self.pathfinder.path_points):
                        next_draw = self.pathfinder.path_points[i + 1] - active_room.offset
                        pygame.draw.line(surface, (255, 210, 80), (draw_point.x, draw_point.y),
                                         (next_draw.x, next_draw.y), 3)

            # если игрок в радиусе атаки начинаем заряжать рывок
            if dist_to_player < self.attack_range and self._state_timer <= 0:
                self.state = "charge"
                self._state_timer = self.pre_attack_cooldown
                self.body.vx = 0.0
                self.body.vy = 0.0
                self.dash_dir = dir_to_player.copy()
            else:
                direction = Vector2(dx, dy)

                if direction.magnitude() < self.aggr_range and direction.magnitude() != 0:
                    direction = direction.normalize()
                    dx, dy = direction
                else:
                    direction = Vector2(0)
                    dx, dy = direction

                # вычисляем ускорение из pathfinder'а
                if dx != 0.0 or dy != 0.0:
                    ax = dx * self.acceleration
                    ay = dy * self.acceleration
                else:
                    ax = ay = 0.0
                    # применяем трение
                    damping = math.exp(-self.friction * dt)
                    self.body.vx *= damping
                    self.body.vy *= damping

                # интегрируем ускорение в скорость
                self.body.vx += ax * dt
                self.body.vy += ay * dt

                # ограничиваем максимальную скорость
                current_speed = self.body.velocity.magnitude()
                if current_speed > self.max_speed:
                    scale = self.max_speed / current_speed
                    self.body.vx *= scale
                    self.body.vy *= scale

                # защита от дрейфа
                if current_speed < 2.0:
                    self.body.vx = 0.0
                    self.body.vy = 0.0

        elif self.state == 'charge':  # готовится к рывку
            self.body.vx = 0.0
            self.body.vy = 0.0
            self.dash_dir = dir_to_player.copy()
            # делаем рывок
            if self._state_timer <= 0:
                self.state = "dash"
                self._state_timer = self.dash_duration
                self.body.vx = self.dash_dir.x * self.dash_speed
                self.body.vy = self.dash_dir.y * self.dash_speed

        elif self.state == "dash": # рывок
            # сбрасываем рывок при контакте или по истечению таймера
            if self.attack_hitbox.colliderect(state.player.rect) or self._state_timer <= 0:
                if self.attack_hitbox.colliderect(state.player.rect):
                    state.player.take_damage(self.attack_damage)
                    self._damage_timer = self.damage_cooldown

                self.state = "recovery"
                self._state_timer = self.post_attack_cooldown
                self.body.vx = 0.0
                self.body.vy = 0.0

        elif self.state == "recovery": # перерыв после рывка
            if self._state_timer <= 0:
                self.state = "chase"
                self._state_timer = self.between_dash_cooldown

        elif self.state == "death": # процесс умирания
            self._shake_amount = 1 - self._state_timer / self.death_duration
            self.body.vx = 0.0
            self.body.vy = 0.0

            if self._state_timer <= 0:
                self.is_alive = False


        # контактный урон
        if self.attack_hitbox.colliderect(state.player.rect) and self.state == "chase":
            if self._damage_timer <= 0:
                state.player.take_damage(self.contact_damage)
                self._damage_timer = self.damage_cooldown

        # обновляем позицию
        self.body.rect.x += self.body.vx * dt
        self.body.rect.y += self.body.vy * dt

        self.attack_hitbox.x = self.body.rect.x - 1
        self.attack_hitbox.y = self.body.rect.y - 1

    # переопределённый метод получения урона
    def take_damage(self, amount: float) -> bool:
        damage = max(0, amount - self.defence)
        self.hp -= damage
        if self.hp <= 0 and self.state != 'death':
            self.state = "death"
            self._state_timer = self.death_duration

        if damage > 0:
            self._visual_damage_timer = self._visual_damage_cooldown

        return damage

    def on_death(self, state: GameState) -> None:
        # спавним декали
        for _ in range(random.randint(7, 10)):
            random_size = random.randint(-3, 5)

            rand_x = random.uniform(-self.rect.width * 1.5, self.rect.width * 1.5)
            rand_y = random.uniform(-self.rect.width * 1.5, self.rect.width * 1.5)
            rand_offset = Vector2(rand_x, rand_y)

            decal = Decal(
                pos=Vector2(self.body.rect.center) + rand_offset,
                lifetime=3,
                size_x=self.body.rect.width + random_size,
                size_y=self.body.rect.width + random_size,
                angle= random.uniform(0, 360),
                sprite=state.assets['hit_decal'],
                fade_time=1,
                max_alpha=150,
            )

            state.decals_system.decals.append(decal)

        for _ in range(random.randint(3, 7)):
            size = int(random.uniform(15, 25))

            rand_x = random.uniform(-self.rect.width, self.rect.width)
            rand_y = random.uniform(-self.rect.width, self.rect.width)

            bookworm = BookWorm(
                x=self.rect.centerx + rand_x,
                y=self.rect.centery + rand_y,
                size_x=size,
                size_y=int(size * 0.75),
                level=config.LEVEL_COEF ** state.level_number * 0.2,
                sprite=state.assets['bookworm_sprite']
            )

            state.enemy_system.enemies.append(bookworm)
