from models.collectable import *
from models.collidable import CollisionBody
from models.decal import Decal
from models.game_state import GameState
from services.pathfinder import Pathfinder
from services.status_manager import StatusManager


class Enemy():
    def __init__(self, x: float, y: float, size_x: int, size_y: int,
                 state: GameState, enemy_type: str = "") -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x - size_x / 2, y - size_y / 2, size_x, size_y),
            layer="dynamic",
            tags={"enemy", enemy_type}
        )
        self._state = state

        self.status_manager = StatusManager(state, self)

        self.attack_hitbox = pygame.Rect(
                self.body.rect.x - 1,
                self.body.rect.y - 1,
                self.body.rect.width + 2,
                self.body.rect.height + 2
            )
        self._source_sprite = pygame.Surface((self.body.rect.width, self.body.rect.height))
        self.sprite = self._source_sprite.copy()
        self.mask = pygame.mask.from_surface(self.sprite)

        self.type = enemy_type
        self.hp = 0.0
        self.max_hp = 0.0
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

        self.slash_marked = False
        self.slash_killed = False

    def update(self, dt: float, surface: pygame.Surface) -> None:
        if self.slash_marked and random.randint(0, 100) < 20:
            self._state.particle_system.spawn_slash_marked(self.rect.center, max(self.rect.width, self.rect.height))

        # обновление статусов
        self.status_manager.update(dt)

    def update_timers(self, dt: float) -> None:
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

    def take_damage(self, amount: float, no_defence: bool=False) -> bool:
        if not no_defence: damage = max(0.0, amount - self.defence)
        else: damage = amount
        self.hp -= damage

        if self.hp <= 0:
            self.is_alive = False
            self._state.stattracker.kills += 1

        if damage > 0:
            self._visual_damage_timer = self._visual_damage_cooldown

        return damage

    def render(self, surface: pygame.Surface) -> None:
        bx, by = self.body.rect.x, self.body.rect.y - (self.body.rect.height - self.sprite.get_height() + 5)
        bw, bh = self.body.rect.width, 3
        if self.hp != self.max_hp:
            pygame.draw.rect(surface, (30, 12, 12), (bx, by, bw, bh))
            pygame.draw.rect(surface, (255, 100, 100), (bx, by, bw * (self.hp / self.max_hp), bh))

    def drop(self):
        pass

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect


class BookWorm(Enemy):
    def __init__(self, x: float, y: float, size_x: int, size_y: int, sprite: pygame.Surface,
                 state: GameState, enemy_type: str = "bookworm", level: float = 1.0, search_index: int = 0) -> None:
        super().__init__(x, y, size_x, size_y, state, enemy_type)
        self._source_sprite = pygame.transform.scale(sprite, (size_x, size_y)).convert_alpha()
        self.sprite = self._source_sprite
        self.body.shadow_offset = -5

        # определяем статы
        self.level = level
        self.hp = 20 * level
        self.max_hp = 20 * level
        self.max_hp = 20 * level
        self.max_speed = 500
        self.defence = 0.0
        self.dash_speed = 2000
        self.attack_damage = 20 * level * 0.5
        self.contact_damage = 25 * level * 0.2
        self.attack_range = 200
        self.aggr_range = 1000
        self.impact_color = (200, 0, 0)
        self.search_index: int = 0

        self.state: str = 'recovery'  # chase, charge, dash, recovery, stun
        self._state_timer = 0.5
        self.dash_dir = Vector2(0)
        self.pre_attack_cooldown = 0.5              # кд перед рывком
        self.post_attack_cooldown = 0.2             # кд после рывка
        self.between_dash_cooldown = 2.0 / level    # кд между рывками
        self.dash_duration = 0.2                    # длительность рывка

        self.acceleration = 2500
        self.friction = config.FRICTION * 10
        self.next_point = Vector2(self.body.center)

        self._repath_cooldown = 0.5

    def take_damage(self, amount: float, no_defence: bool = False) -> None:
        super().take_damage(amount, no_defence)

        self._state.audio_manager.play_sound(f'bookworm_damaged_{random.randint(1, 4)}')

    def render(self, surface: pygame.Surface) -> None:
        super().render(surface)
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

    def update(self, dt: float, surface: pygame.Surface) -> None:
        super().update(dt, surface)

        # обновляем таймеры
        active_room = self._state.room_manager.active_room
        self.update_timers(dt)

        # если ещё остались точки
        if self.pathfinder.path_points:
            distance = Vector2(self.body.rect.center).distance_to(Vector2(self.next_point))
            if distance <= config.TILE_SIZE - 5 and len(self.pathfinder.path_points) > 1:
                self.next_point = Vector2(self.pathfinder.path_points.pop(0))
                pygame.draw.circle(surface, (32, 255, 28), self.next_point - active_room.offset, 7)
        else:
            self.next_point = Vector2(self.body.rect.center)

        # Вектор и дистанция до игрока
        dist_to_player = Vector2(self.rect.center).distance_to(self._state.player.rect.center)
        if dist_to_player != 0:
            dir_to_player = (pygame.Vector2(self._state.player.rect.center) - pygame.Vector2(self.rect.center)).normalize()
        else:
            dir_to_player = Vector2(0, 0)

        # Обрабатываем логику по состояниям
        if not self.state == 'stun':
            if self.state == 'chase':  # поиск игрока
                dx = self.next_point.x - self.body.rect.centerx
                dy = self.next_point.y - self.body.rect.centery

                # обновляем данные с pathfinder'а
                if self._repath_timer <= 0:
                    self._state.audio_manager.play_sound(f'bookworm_step_{random.randint(1, 4)}')

                    self._repath_timer = self._repath_cooldown
                    if self.pathfinder.search_path(Vector2(self.rect.center), Vector2(self._state.player.rect.center), active_room,
                                                search_index=self.search_index):
                        self.is_alive = False
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
                    self._state.audio_manager.play_sound(f'bookworm_dash_{random.randint(1, 3)}', 1.3)

            elif self.state == "dash":
                self._state.particle_system.spawn_while_dash(self.rect.center, self.dash_dir,
                                                             (220, 220, 220), self.rect.height)

                # сбрасываем рывок при контакте или по истечению таймера
                if self.attack_hitbox.colliderect(self._state.player.rect) or self._state_timer <= 0:
                    if self.attack_hitbox.colliderect(self._state.player.rect) and not self._state.player.ignore_enemy:
                        self._state.player.take_damage(self.attack_damage)
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
            if (self.attack_hitbox.colliderect(self._state.player.rect) and self.state == "chase"
                    and not  self._state.player.ignore_enemy):
                if self._damage_timer <= 0:
                    self._state.player.take_damage(self.contact_damage)
                    self._damage_timer = self.damage_cooldown

            # обновляем позицию
            vel = self.body.velocity.magnitude()
            if vel * dt > config.TILE_SIZE / 2:
                self._state.collision_system.sub_step_moving(self.body, dt, vel)
            else:
                self.body.rect.x += self.body.vx * dt
                self.body.rect.y += self.body.vy * dt

            self.attack_hitbox.x = self.body.rect.x - 1
            self.attack_hitbox.y = self.body.rect.y - 1
        else:
            if self._state_timer <= 0:
                self.state = "chase"

    def on_death(self) -> None:
        random_size = random.randint(-3, 5)
        decal = Decal(
            pos=Vector2(self.body.rect.center),
            lifetime=15,
            size_x=self.body.rect.width + random_size,
            size_y=self.body.rect.width + random_size,
            angle= random.uniform(0, 360),
            sprite=self._state.assets['hit_decal'],
            fade_time=1,
            max_alpha=150,
        )

        self._state.decals_system.decals.append(decal)
        self._state.audio_manager.play_sound(f'bookworm_death_{random.randint(1, 4)}', 1.7)
        self._state.audio_manager.play_sound(f'bookworm_death_{random.randint(1, 4)}', 1.7)
        self._state.audio_manager.play_sound(f'bookworm_death_{random.randint(1, 4)}', 1.7)

        self.drop()

    # спавним дроп
    def drop(self) -> None:
        if self._state.player.hp != self._state.player.max_hp:
            # спавним хилки
            count = random.randint(int(2 * self.level), int(3 * self.level))
            for _ in range(count):
                self._state.collectable_system.items.append(EnergyCell(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=7,
                    lifetime=10,
                    max_speed=600,
                    collect_range=300
                ))

            # с шансом 50% спавним скрап
            if random.randint(1, 100) <= 50:
                count = random.randint(int(2 * self.level), int(3 * self.level))
                for _ in range(count):
                    self._state.collectable_system.items.append(Scrap(
                        x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                        y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                        size=6,
                        lifetime=10,
                        max_speed=300,
                        collect_range=300,
                        sprites=self._state.assets['scrap_sprites']
                    ))
        # гарантированный скрап если игрок не ранен
        else:
            count = random.randint(int(2 * self.level), int(3 * self.level))
            for _ in range(count):
                self._state.collectable_system.items.append(Scrap(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=6,
                    lifetime=10,
                    max_speed=300,
                    collect_range=300,
                    sprites=self._state.assets['scrap_sprites']
                ))
        # доп дроп при добивании слешером
        if self.slash_killed:
            count = int(self.level)
            for _ in range(count):
                self._state.collectable_system.items.append(Scrap(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=6,
                    lifetime=10,
                    max_speed=300,
                    collect_range=300,
                    sprites=self._state.assets['scrap_sprites']
                ))

            count = random.randint(int(self.level), int(2 * self.level))
            for _ in range(count):
                self._state.collectable_system.items.append(EnergyCell(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=7,
                    lifetime=10,
                    max_speed=600,
                    collect_range=300
                ))


class BookWormMommy(Enemy):
    def __init__(self, x: float, y: float, size_x: int, size_y: int, sprite: pygame.Surface,
                 state: GameState, enemy_type: str = "bookworm", level: float = 1.0, search_index: int = 0) -> None:
        super().__init__(x, y, size_x, size_y, state, enemy_type)
        self._source_sprite = pygame.transform.scale(sprite, (size_x, size_y)).convert_alpha()
        self.sprite = self._source_sprite
        self.body.shadow_offset = -10

        # определяем статы
        self.level = level
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
        self.search_index = search_index

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
        super().render(surface)
        # зеркалирование
        if self.body.vx < 0 and self._facing_right:
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self._source_sprite = pygame.transform.flip(self._source_sprite, True, False)
            self._facing_right = False
        elif self.body.vx > 0 and not self._facing_right:
            self.sprite = pygame.transform.flip(self.sprite, True, False)
            self._source_sprite = pygame.transform.flip(self._source_sprite, True, False)
            self._facing_right = True

        sprite = self.sprite.copy().convert_alpha()
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

        # for color in self.status_manager.get_status_colors():
        #     print(color)
        #     sprite.fill(color, None, pygame.BLEND_RGBA_MULT)

        surface.blit(sprite, (self.rect.x + offset_x, self.rect.y + offset_y))
        self.sprite = self._source_sprite.copy().convert_alpha()

    def update(self, dt: float, surface: pygame.Surface) -> None:
        super().update(dt, surface)

        # обновляем таймеры
        active_room = self._state.room_manager.active_room
        self.update_timers(dt)

        # если ещё остались точки
        if self.pathfinder.path_points:
            distance = Vector2(self.body.rect.center).distance_to(Vector2(self.next_point))
            if distance <= config.TILE_SIZE - 5 and len(self.pathfinder.path_points) > 1:
                self.next_point = Vector2(self.pathfinder.path_points.pop(0))
                pygame.draw.circle(surface, (32, 255, 28), self.next_point - active_room.offset, 7)
        else:
            self.next_point = Vector2(self.body.rect.center)

        # Вектор и дистанция до игрока
        dist_to_player = Vector2(self.rect.center).distance_to(self._state.player.rect.center)
        if dist_to_player != 0:
            dir_to_player = (pygame.Vector2(self._state.player.rect.center) - pygame.Vector2(self.rect.center)).normalize()
        else:
            dir_to_player = Vector2(0, 0)

        # Обрабатываем логику по состояниям
        if not self.state == 'stun':
            if self.state == 'chase':  # поиск игрока
                dx = self.next_point.x - self.body.rect.centerx
                dy = self.next_point.y - self.body.rect.centery

                # обновляем данные с pathfinder'а
                if self._repath_timer <= 0:
                    self._state.audio_manager.play_sound(f'bookworm_step_{random.randint(1, 4)}')
                    self._repath_timer = self._repath_cooldown
                    if self.pathfinder.search_path(Vector2(self.rect.center), Vector2(self._state.player.rect.center), active_room,
                                                search_index=self.search_index):
                        self.is_alive = False
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
                    self._state.audio_manager.play_sound(f'bookworm_dash_{random.randint(1, 3)}', 1.3)

            elif self.state == "dash": # рывок
                self._state.particle_system.spawn_while_dash(self.rect.center, self.dash_dir,
                                                             (220, 220, 220), self.rect.height)

                # сбрасываем рывок при контакте или по истечению таймера
                if (self.attack_hitbox.colliderect(self._state.player.rect) or self._state_timer <= 0
                        and not self._state.player.ignore_enemy):
                    if self.attack_hitbox.colliderect(self._state.player.rect):
                        self._state.player.take_damage(self.attack_damage)
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

                self._state.camera.shake(self._shake_amount * 10, 0.1)

                if self._state_timer <= 0:
                    self.is_alive = False

            # контактный урон
            if (self.attack_hitbox.colliderect(self._state.player.rect) and self.state == "chase"):
                if self._damage_timer <= 0:
                    self._state.player.take_damage(self.contact_damage)
                    self._damage_timer = self.damage_cooldown

            # обновляем позицию
            vel = self.body.velocity.magnitude()
            if vel * dt > config.TILE_SIZE / 2:
                self._state.collision_system.sub_step_moving(self.body, dt, vel)
            else:
                self.body.rect.x += self.body.vx * dt
                self.body.rect.y += self.body.vy * dt

                self.attack_hitbox.x = self.body.rect.x - 1
                self.attack_hitbox.y = self.body.rect.y - 1
        else:
            if self._state_timer <= 0:
                self.state = "chase"

    # переопределённый метод получения урона
    def take_damage(self, amount: float, no_defence: bool = False) -> bool:
        if not no_defence: damage = max(0.0, amount - self.defence)
        else: damage = amount
        if damage: self._visual_damage_timer = self._visual_damage_cooldown
        self.hp -= damage
        self._state.audio_manager.play_sound(f'bookworm_damaged_{random.randint(1, 4)}', 1.2)
        if self.hp <= 0 and self.state != 'death':
            self.state = "death"
            self._state_timer = self.death_duration
            self._state.audio_manager.play_sound('mommy_pre_explode')

        return damage

    def on_death(self) -> None:
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
                sprite=self._state.assets['hit_decal'],
                fade_time=1,
                max_alpha=150,
            )

            self._state.decals_system.decals.append(decal)
            self._state.audio_manager.play_sound('mommy_explode', 0.8)
            self._state.audio_manager.play_sound(f'bookworm_death_{random.randint(1, 4)}', 1.3)
            self._state.audio_manager.play_sound(f'bookworm_death_{random.randint(1, 4)}', 1.3)

        for _ in range(random.randint(3, 7)):
            size = int(random.uniform(15, 25))

            rand_x = random.uniform(-self.rect.width, self.rect.width)
            rand_y = random.uniform(-self.rect.width, self.rect.width)
            sprite = self._state.assets['bookworm_sprite'].copy()
            sprite.convert_alpha()
            sprite.fill((150, 30, 30), None, pygame.BLEND_RGB_ADD)

            bookworm = BookWorm(
                x=self.rect.centerx + rand_x,
                y=self.rect.centery + rand_y,
                size_x=size,
                size_y=int(size * 0.75),
                level=config.LEVEL_COEF ** self._state.level_number * 0.2,
                sprite=sprite,
                state=self._state
            )

            self._state.enemy_system.enemies.append(bookworm)

        # спавним дроп
        self.drop()

        # трясём камеру
        self._state.camera.shake(10, 0.15)

    def drop(self):
        # спавним дроп
        if self._state.player.hp != self._state.player.max_hp:
            # спавним хилки
            count = random.randint(int(2 * self.level), int(3 * self.level))
            for _ in range(count):
                self._state.collectable_system.items.append(EnergyCell(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=7,
                    lifetime=10,
                    max_speed=600,
                    collect_range=300
                ))

            # с шансом 80% спавним скрап
            if random.randint(1, 100) <= 80:
                count = random.randint(int(2 * self.level), int(4 * self.level))
                for _ in range(count):
                    self._state.collectable_system.items.append(Scrap(
                        x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                        y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                        size=6,
                        lifetime=10,
                        max_speed=300,
                        collect_range=300,
                        sprites=self._state.assets['scrap_sprites']
                    ))
        # гарантированный скрап если игрок не ранен
        else:
            count = random.randint(int(self.level), int(2 * self.level))
            for _ in range(count):
                self._state.collectable_system.items.append(Scrap(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=6,
                    lifetime=10,
                    max_speed=300,
                    collect_range=300,
                    sprites=self._state.assets['scrap_sprites']
                ))

        if random.randint(1, 100) <= 80:
            item = random.choice(self._state.drop_pool)
            self._state.collectable_system.items.append(item[0](
                x=self.rect.centerx,
                y=self.rect.centery,
                size=35,
                lifetime=15,
                max_speed=1000,
                vx=0,
                vy=0,
                acceleration=-5,
                magnet=False,
                collect_range=300,
                sprite=self._state.assets[item[1]],
            ))

        # доп дроп при добивании слешером
        if self.slash_killed:
            count = random.randint(int(self.level), int(2 * self.level))
            for _ in range(count):
                self._state.collectable_system.items.append(Scrap(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=6,
                    lifetime=10,
                    max_speed=300,
                    collect_range=300,
                    sprites=self._state.assets['scrap_sprites']
                ))

            count = int(self.level)
            for _ in range(count):
                self._state.collectable_system.items.append(EnergyCell(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=7,
                    lifetime=10,
                    max_speed=600,
                    collect_range=300
                ))
