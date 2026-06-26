from models.projectile import *


# общий класс
class Weapon:
    def __init__(self, state: GameState, name: str) -> None:
        self._state = state
        self.signature_color = state.player.signature_color

        self.name = name
        self.sprite = state.assets[self.name]
        self.reload_sprite = state.assets[f'{self.name}_reload']
        self.crosshair = state.assets[f'{self.name}_crosshair']

        self.offset_x: float = 0
        self.offset_y: float = 0
        self.facing_right = True
        self.angle = 0

        self.is_reloading = False
        self.reload_timer = 0.0
        self.reload_cooldown = 1.0

        self.is_autofired: bool = True

        self.power = 25
        self.damage_coef = 1.0

        self.level = 1
        self.upgrade_cost = 10
        self.can_upgrade = True

        # ключевые параметры из трех переменных
        self.name_param_1 = ''
        self._param_1 = 0.0
        self.min_param_1 = 0.0
        self.max_param_1 = 0.0
        self.coef_param_1 = 0.0


        self.name_param_2 = ''
        self._param_2 = 0.0
        self.min_param_2 = 0.0
        self.max_param_2 = 0.0
        self.coef_param_2 = 0.0

        self.name_param_3 = ''
        self._param_3 = 0.0
        self.min_param_3 = 0.0
        self.max_param_3 = 0.0
        self.coef_param_3 = 0.0

        self.clip_size = 0
        self.clip = 0

    @property
    def param_1(self) -> float:
        return self._param_1 * self.coef_param_1

    @param_1.setter
    def param_1(self, value: float) -> None:
        delta = self._param_1 - value
        if delta > 0:  # уменьшение
            if value < self.min_param_1:
                self._param_1 = self.min_param_1
            else:
                self._param_1 = value

            if self._param_2 < self.max_param_2:
                self._param_2 = self.power / (self._param_3 * self._param_1)

                if self._param_2 > self.max_param_2:
                    self._param_2 = self.max_param_2
                    self._param_3 = self.power / (self._param_1 * self._param_2)

            else:
                self._param_3 = self.power / (self._param_1 * self._param_2)

        else:  # увеличение
            if value > self.max_param_1:
                self._param_1 = self.max_param_1
            else:
                self._param_1 = value

            if self._param_3 > self.min_param_3:
                self._param_3 = self.power / (self._param_2 * self._param_1)

                if self._param_3 < self.min_param_3:
                    self._param_3 = self.min_param_3
                    self._param_2 = self.power / (self._param_3 * self._param_1)

            else:
                self._param_2 = self.power / (self._param_3 * self._param_1)

    @property
    def param_2(self) -> float:
        return self._param_2 * self.coef_param_2

    @param_2.setter
    def param_2(self, value: float) -> None:
        delta = self._param_2 - value
        if delta > 0:  # уменьшение
            if value < self.min_param_2:
                self._param_2 = self.min_param_2
            else:
                self._param_2 = value

            if self._param_3 < self.max_param_3:
                self._param_3 = self.power / (self._param_2 * self._param_1)

                if self._param_3 > self.max_param_3:
                    self._param_3 = self.max_param_3
                    self._param_1 = self.power / (self._param_3 * self._param_2)

            else:
                self._param_1 = self.power / (self._param_3 * self._param_2)

        else:  # увеличение
            if value > self.max_param_2:
                self._param_2 = self.max_param_2
            else:
                self._param_2 = value

            if self._param_1 > self.min_param_1:
                self._param_1 = self.power / (self._param_3 * self._param_2)

                if self._param_1 < self.min_param_1:
                    self._param_1 = self.min_param_1
                    self._param_3 = self.power / (self._param_2 * self._param_1)

            else:
                self._param_3 = self.power / (self._param_2 * self._param_1)

    @property
    def param_3(self) -> float:
        return self._param_3 * self.coef_param_3

    @param_3.setter
    def param_3(self, value: float) -> None:
        delta = self._param_3 - value
        if delta > 0:  # уменьшение
            if value < self.min_param_3:
                self._param_3 = self.min_param_3
            else:
                self._param_3 = value

            if self._param_1 < self.max_param_1:
                self._param_1 = self.power / (self._param_3 * self._param_2)

                if self._param_1 > self.max_param_1:
                    self._param_1 = self.max_param_1
                    self._param_2 = self.power / (self._param_3 * self._param_1)

            else:
                self._param_2 = self.power / (self._param_3 * self._param_1)

        else:  # увеличение
            if value > self.max_param_3:
                self._param_3 = self.max_param_3
            else:
                self._param_3 = value

            if self._param_2 > self.min_param_2:
                self._param_2 = self.power / (self._param_3 * self._param_1)

                if self._param_2 < self.min_param_2:
                    self._param_2 = self.min_param_2
                    self._param_1 = self.power / (self._param_3 * self._param_2)

            else:
                self._param_1 = self.power / (self._param_3 * self._param_2)

    def calculate_max(self) -> None:
        self.max_param_1 = round(self.power / (self.min_param_2 * self.min_param_3), 1)
        self.max_param_2 = round(self.power / (self.min_param_1 * self.min_param_3), 1)
        self.max_param_3 = round(self.power / (self.min_param_1 * self.min_param_2), 1)

        self._param_2 = round(self.power / (self._param_1 * self._param_3), 1)

    @property
    def fire_rate(self) -> float:
        pass

    # отрисовка
    def render(self, surface: pygame.Surface,
               mouse_world_pos: pygame.Vector2, player_pos: pygame.Vector2) -> None:
        # обычное отображение
        if not self.is_reloading:
            dx = mouse_world_pos.x - player_pos.x
            dy = mouse_world_pos.y - player_pos.y
            angle = math.degrees(math.atan2(dy, dx))

            # зеркалирование
            weapon_sprite = self.sprite
            offset_x = self.offset_x
            if not self.facing_right:
                weapon_sprite = pygame.transform.flip(self.sprite, False, True)
                offset_x = -offset_x

            # вращаем спрайт оружия
            rotated = pygame.transform.rotate(weapon_sprite, -angle)


        # анимация перезарядки
        else:
            self.angle += 40

            # зеркалирование
            weapon_sprite = self.reload_sprite
            offset_x = self.offset_x
            if not self.facing_right:
                weapon_sprite = pygame.transform.flip(self.reload_sprite, False, True)
                offset_x = -offset_x

            # вращаем спрайт оружия
            rotated = pygame.transform.rotate(weapon_sprite, -self.angle)

        # позиционируем оружие
        wx = player_pos.x - rotated.get_width() / 2 + offset_x
        wy = player_pos.y - rotated.get_height() / 2 + self.offset_y

        surface.blit(rotated, (wx, wy))

    def update(self, dt: float) -> None:
        pass

    def draw_crosshair(self, screen: pygame.Surface) -> None:
        pos = pygame.mouse.get_pos()
        ox = self.crosshair.get_width() // 2
        oy = self.crosshair.get_height() // 2
        screen.blit(self.crosshair, (pos[0] - ox, pos[1] - oy))


# slasher
class Pointer(Weapon):
    def __init__(self, state: GameState) -> None:
        super().__init__(state, 'pointer')
        self._state = state
        self.offset_x = 15

        # балансировочные переменные
        """балансировочная формула:
            power = const; power = damage * fire_rate; damage = size * speed
            +speed = -fire_rate
            +size = -speed
            +fire_rate = -size"""
        # ключевые параметры из трех переменных
        self.name_param_1 = 'Bullet size'
        self._param_1 = 2.0 # px
        self.min_param_1 = 2.0
        self.max_param_1 = 0.0
        self.coef_param_1 = 5.0

        self.name_param_2 = 'Fire rate'
        self._param_2 = 3.0
        self.min_param_2 = 3.0
        self.max_param_2 = 0.0
        self.coef_param_2 = 1.0

        self.name_param_3 = 'Bullet speed'
        self._param_3 = 2.0
        self.min_param_3 = 2.0
        self.max_param_3 = 0.0
        self.coef_param_3 = 200.0

        self.power = 25
        self.damage_coef = 0.7
        self.calculate_max()

        self.clip_size = 5
        self.clip = 5

        self.level = 1
        self.upgrade_cost = 10
        self.can_upgrade = True

    def upgrade(self):
        self.level += 1
        if self.level % 2 == 0:
            self.upgrade_cost += 10
            self.power += 5
            
        if self.level % 4 == 0:
            self.clip_size += 5
            self.damage_coef += 0.05

        self.calculate_max()

        if self.power >= config.MAX_POWER_LIMIT:
            self.power = config.MAX_POWER_LIMIT
            self.can_upgrade = False

        self._state.audio_manager.play_sound('weapon_upgrade')

    @property
    def damage(self) -> float:
        return self._param_3 * self._param_1 * self.damage_coef

    def fire(self) -> None:
        offset_coef = self.offset_x + (self._param_1 * self.coef_param_1) / 2

        origin = pygame.Vector2(self._state.player.rect.centerx, self._state.player.rect.centery)
        direction = self._state.player.mouse_world_pos - origin
        angle = random.uniform(-3, 3)
        spawn_pos = origin + direction.normalize() * offset_coef
        direction = direction.rotate(angle)

        if direction.magnitude() == 0:
            direction = pygame.Vector2(1, 0)

        speed = self.param_3
        vel = direction.normalize() * speed

        projectile = PointerProjectile(
            state=self._state,
            x=spawn_pos.x, y=spawn_pos.y,
            size=self.param_1,
            velocity=vel,
            damage=self.damage,
            lifetime=10.0
        )
        self._state.projectile_system.projectiles.append(projectile)
        self._state.audio_manager.play_sound('pointer_shot')

    @property
    def fire_rate(self) -> float:
        return self._param_2


# electron
class Tazer(Weapon):
    def __init__(self, state: GameState) -> None:
        super().__init__(state, 'tazer')
        self._state = state
        self.offset_x = 15

        # балансировочные переменные
        """балансировочная формула:
            power = const; power * shock = fire_rate * speed; damage = speed/shock; shock = fire_rate * speed / power 
            +shock = -fire_rate
            +speed = -shock
            +fire_rate = -speed"""
        # ключевые параметры из трех переменных
        self.name_param_1 = 'Shock'
        self._param_1 = 2.0  # electrified points
        self.min_param_1 = 2.0
        self.max_param_1 = 0.0
        self.coef_param_1 = 1.3

        self.name_param_2 = 'Fire rate'
        self._param_2 = 1.0
        self.min_param_2 = 1.0
        self.max_param_2 = 0.0
        self.coef_param_2 = 1.0

        self.name_param_3 = 'Bullet speed'
        self._param_3 = 3.0
        self.min_param_3 = 3.0
        self.max_param_3 = 0.0
        self.coef_param_3 = 100.0

        self.power = 25
        self.damage_coef = 0.5
        self.calculate_max()

        self.reload_cooldown = 0.75

        self.clip_size = 12
        self.clip = 12

        self.level = 1
        self.upgrade_cost = 10
        self.can_upgrade = True

        self.is_autofired: bool = False

        self.is_fire = False
        self._burst_timer = 0.0
        self._burst_time = 0.15
        self._burst_counter = 0

    def upgrade(self):
        self.level += 1
        if self.level % 2 == 0:
            self.upgrade_cost += 10
            self.power += 5

        if self.level % 3 == 0:
            self.clip_size += 3
            self.damage_coef += 0.05

        self.calculate_max()

        if self.power >= config.MAX_POWER_LIMIT:
            self.power = config.MAX_POWER_LIMIT
            self.can_upgrade = False

        self._state.audio_manager.play_sound('weapon_upgrade')

    def update(self, dt: float) -> None:
        if self.is_fire:
            self._burst_timer -= dt

            if self._burst_timer < self._burst_time / 2 and self._burst_counter == 1:
                self.spawn_projectile()
                self.clip -= 1

            if self._burst_timer < 0:
                self.spawn_projectile()
                self.is_fire = False
                self._burst_counter = 0
                self.clip -= 1

    def calculate_max(self) -> None:
        self.max_param_1 = round(self.power / (self.min_param_2 * self.min_param_3), 1)
        self.max_param_2 = round(self.power / (self.min_param_1 * self.min_param_3), 1)
        self.max_param_3 = round(self.power / (self.min_param_1 * self.min_param_2), 1)

        self._param_3 = round(self.power / (self._param_1 * self._param_2), 1)

    def fire(self) -> None:
        if not self.is_fire:
            self.is_fire = True
            self._burst_timer = self._burst_time
            self.spawn_projectile()

    @property
    def fire_rate(self) -> float:
        return self._param_2

    def spawn_projectile(self) -> None:
        self._burst_counter += 1
        offset_coef = self.sprite.get_width() - self.offset_x * 3

        origin = pygame.Vector2(self._state.player.rect.centerx, self._state.player.rect.centery)
        direction = self._state.player.mouse_world_pos - origin
        angle = random.uniform(-1, 1)
        spawn_pos = origin + direction.normalize() * offset_coef
        direction = direction.rotate(angle)

        if direction.magnitude() == 0:
            direction = pygame.Vector2(1, 0)

        speed = self.param_3
        vel = direction.normalize() * speed

        projectile = TazerProjectile(
            state=self._state,
            x=spawn_pos.x, y=spawn_pos.y,
            size=15,
            velocity=vel,
            damage=self.damage / 3,
            lifetime=10.0
        )
        self._state.projectile_system.projectiles.append(projectile)
        self._state.audio_manager.play_sound('tazer_shot')

    @property
    def damage(self) -> float:
        return self.power / self._param_1 / self._param_2 * self.damage_coef

    @property
    def electrified_points(self) -> float:
        return (self._param_1) * self.coef_param_1


# tank
class Bulldog(Weapon):
    def __init__(self, state: GameState) -> None:
        super().__init__(state, 'bulldog')
        self._state = state
        self.offset_x = 15

        self.crosshair_side_r = state.assets['bulldog_crosshair_side']
        self.crosshair_side_l = pygame.transform.flip(self.crosshair_side_r, True, False)
        self.crosshair_cursor = state.assets['bulldog_crosshair_cursor']

        '''
        bullet_count = min + (max - min) * (spread / spread_max)
        '''

        self.bullet_count_min = 2
        self.bullet_count_max = 22

        self.name_param_1 = 'Spread angle'
        self._param_1 = 2.0
        self.min_param_1 = 1.0
        self.max_param_1 = 5.0
        self.coef_param_1 = 10

        self.name_param_2 = 'Fire rate'
        self._param_2 = 1.0
        self.min_param_2 = 1.0
        self.max_param_2 = 0.0
        self.coef_param_2 = 1.0

        self.name_param_3 = 'Destructive'
        self._param_3 = 1.0
        self.min_param_3 = 1.0
        self.max_param_3 = 0.0
        self.coef_param_3 = 1.0

        self.power = 25
        self.power_coef = 0.5
        self.damage_coef = 1.0
        self.calculate_max()

        self.reload_cooldown = 1.2

        self.clip = 4
        self.clip_size = 4

        self.level = 1
        self.upgrade_cost = 10
        self.can_upgrade = True

        self.is_autofired: bool = True

    def upgrade(self):
        self.level += 1
        if self.level % 2 == 0:
            self.upgrade_cost += 10
            self.power += 5

        if self.level % 4 == 0:
            self.clip_size += 2
            self.damage_coef += 0.05

        self.calculate_max()

        if self.power >= config.MAX_POWER_LIMIT:
            self.power = config.MAX_POWER_LIMIT
            self.can_upgrade = False

        self._state.audio_manager.play_sound('weapon_upgrade')

    def calculate_max(self) -> None:
        self.max_param_2 = (self.power ** 0.5 * self.power_coef)
        self.max_param_3 = (self.power ** 0.5 * self.power_coef)
        self.damage_coef = 1 / self.max_param_3

        self._param_2 = self.max_param_2

    @property
    def param_1(self) -> float:
        return self._param_1 * self.coef_param_1

    @param_1.setter
    def param_1(self, value: float) -> None:
        delta = self._param_1 - value
        if delta > 0:  # уменьшение
            if value < self.min_param_1:
                self._param_1 = self.min_param_1
            else:
                self._param_1 = value

        else:  # увеличение
            if value > self.max_param_1:
                self._param_1 = self.max_param_1
            else:
                self._param_1 = value

    @property
    def param_2(self) -> float:
        return self._param_2 * self.coef_param_2

    @param_2.setter
    def param_2(self, value: float) -> None:
        delta = self._param_2 - value
        if delta > 0:  # уменьшение
            if value < self.min_param_2:
                self._param_2 = self.min_param_2
            else:
                self._param_2 = value

        else:  # увеличение
            if value > self.max_param_2:
                self._param_2 = self.max_param_2
            else:
                self._param_2 = value

        self._param_3 = self.power ** 0.5 * self.power_coef / self._param_2

    @property
    def param_3(self) -> float:
        return self._param_3 * self.coef_param_3

    @param_3.setter
    def param_3(self, value: float) -> None:
        delta = self._param_3 - value
        if delta > 0:  # уменьшение
            if value < self.min_param_3:
                self._param_3 = self.min_param_3
            else:
                self._param_3 = value

        else:  # увеличение
            if value > self.max_param_3:
                self._param_3 = self.max_param_3
            else:
                self._param_3 = value

        self._param_2 = self.power ** 0.5 * self.power_coef / self._param_3

    @property
    def bullet_count(self) -> int:
        return int(self.bullet_count_min + (self.bullet_count_max - self.bullet_count_min)
                * (self._param_1 / self.max_param_1))

    @property
    def damage(self) -> tuple[float, int]:
        return (self.power * self._param_3 * self.damage_coef) / self.bullet_count, self.bullet_count

    def draw_crosshair(self, screen: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        offset = self._state.room_manager.active_room.offset
        px, py = ((Vector2(self._state.player.rect.centerx, self._state.player.rect.centery) - offset)
                  * self._state.engine.current_aspect)

        dx = mouse_pos[0] - px
        dy = mouse_pos[1] - py

        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(-angle_rad)

        sprite = pygame.transform.rotate(self.crosshair, angle_deg + 90)
        sprite_r = pygame.transform.rotate(self.crosshair_side_r, angle_deg + 90 + self.param_1 / 2)
        sprite_l = pygame.transform.rotate(self.crosshair_side_l, angle_deg + 90 - self.param_1 / 2)

        render_vector = (mouse_pos - Vector2(px, py)).normalize() * 150
        render_vector_r = render_vector.rotate(-self.param_1 / 2)
        render_vector_l = render_vector.rotate(self.param_1 / 2)

        render_x, render_y = Vector2(px, py) + render_vector
        render_x_r, render_y_r = Vector2(px, py) + render_vector_r
        render_x_l, render_y_l = Vector2(px, py) + render_vector_l

        ox = self.crosshair.get_width() // 2
        oy = self.crosshair.get_height() // 2
        screen.blit(sprite, (render_x - ox, render_y - oy))

        sx = self.crosshair_side_r.get_width() // 2
        sy = self.crosshair_side_r.get_height() // 2
        screen.blit(sprite_r, (render_x_r - ox, render_y_r - oy))
        screen.blit(sprite_l, (render_x_l - ox, render_y_l - oy))

        # отрисовываем курсор
        ox = self.crosshair_cursor.get_width() // 2
        oy = self.crosshair_cursor.get_height() // 2
        screen.blit(self.crosshair_cursor, (mouse_pos[0] - ox, mouse_pos[1] - oy))

    def update(self, _: float) -> None:
        if self._state.player.current_max_speed != self._state.player.max_speed:
            self._state.player.current_max_speed = self._state.player.max_speed

    def fire(self):
        mouse_pos = pygame.mouse.get_pos()
        offset = self._state.room_manager.active_room.offset
        px, py = ((Vector2(self._state.player.rect.centerx, self._state.player.rect.centery) - offset)
                  * self._state.engine.current_aspect)

        recoil_vector = (Vector2(px, py) - mouse_pos).normalize() * 25000 * self.param_3
        self._state.player.current_max_speed = recoil_vector.magnitude()

        self._state.player.body.impulse += recoil_vector

        offset_coef = self.sprite.get_width() - self.offset_x * 3
        for _ in range(self.bullet_count):
            direction = -recoil_vector.rotate(random.uniform(-self.param_1 / 2, self.param_1 / 2))

            origin = pygame.Vector2(self._state.player.rect.centerx, self._state.player.rect.centery)
            spawn_pos = origin + direction.normalize() * offset_coef

            if direction.magnitude() == 0:
                direction = pygame.Vector2(1, 0)

            vel = direction.normalize() * 1500

            projectile = BulldogProjectile(
                state=self._state,
                x=spawn_pos.x, y=spawn_pos.y,
                size=12,
                velocity=vel,
                damage=self.damage[0],
                lifetime=3.0
            )
            self._state.projectile_system.projectiles.append(projectile)
        self._state.audio_manager.play_sound('tazer_shot')


    @property
    def fire_rate(self) -> float:
        return self.param_2

