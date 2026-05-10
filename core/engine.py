import pygame
from pygame import Vector2

import config
from random import randint
from core.asset_manager import AssetManager
from models.game_state import GameState
from controllers.input_handler import InputHandler
from models.player import Player
from models.room_manager import RoomManager
from models.camera import Camera
from models.weapons import *
from services.collision_system import CollisionSystem
from services.decal_system import DecalSystem
from services.enemy_system import EnemySystem
from services.spawner import Spawner
from services.weapon_system import WeaponSystem
from services.projectile_system import ProjectileSystem
from services.particle_system import ParticleSystem
from views.renderer import Renderer
from views.ui_renderer import UIRenderer
from views.map_renderer import MinimapRenderer

# Основной движок
class GameEngine:
    def __init__(self) -> None:
        pygame.init()

        if config.FULLSCREEN:
            # Полный экран: (0, 0) автоматически использует разрешение монитора
            display_flags = pygame.FULLSCREEN
            screen_size = (0, 0)
        else:
            # Оконный режим: используем внутреннее разрешение
            display_flags = 0
            screen_size = (config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT)

        self._screen = pygame.display.set_mode(screen_size, display_flags)
        pygame.display.set_caption(config.WINDOW_TITLE)

        self._hit_pause_frames = 0

        # инициализируем игру
        self._state = GameState()

        # ГРУЗИМ СПРАЙТЫ
        assets_manager = AssetManager()
        self._load_sprites(assets_manager)

        # инициализируем уровень ДО игрока чтобы взять координаты спавна
        self._room_manager = RoomManager(wall_sprite=self._state.assets['wall_sprite'],
                                         floor_sprite=self._state.assets['floor_sprite'])
        spawn_center = self._room_manager.active_room.bounds.center

        # инструменты и системы
        self._clock = pygame.time.Clock()
        self._input = InputHandler(self._state)
        self._collision_system = CollisionSystem()
        self._weapon_system = WeaponSystem()


        self._state.projectile_system = ProjectileSystem(on_wall_impact=self._on_wall_impact,
                                                   on_enemy_impact=self._on_enemy_impact)
        self._state.particle_system = ParticleSystem()
        self._state.enemy_system = EnemySystem()
        self._state.decals_system = DecalSystem()
        self._spawner = Spawner()

        self._camera = Camera()
        self._camera.position = pygame.Vector2(spawn_center)
        self._camera.curr_center = self._camera.position.copy()
        self._camera.prev_center = self._camera.position.copy()

        # определяем точку спавна
        if self._room_manager.start_room:
            spawn_center = self._room_manager.start_room.bounds.center

            self._state.player = Player(
                x=spawn_center[0] - config.PLAYER_SIZE / 2,
                y=spawn_center[1] - config.PLAYER_SIZE / 2,
                sprite=self._state.assets['player_sprite']
            )

            # kамера тоже стартует с центра стартовой комнаты
            self._camera.position = pygame.Vector2(spawn_center)
            self._camera.curr_center = self._camera.position.copy()
            self._camera.prev_center = self._camera.position.copy()
        else:
            # Fallback на случай ошибки генерации
            self._state.player = Player(config.INTERNAL_WIDTH / 2, config.INTERNAL_HEIGHT / 2,
                                        self._state.assets['player_sprite'])
            self._camera.position = pygame.Vector2(config.INTERNAL_WIDTH / 2, config.INTERNAL_HEIGHT / 2)
            self._camera.curr_center = self._camera.position.copy()
            self._camera.prev_center = self._camera.position.copy()

        # рендереры
        self._map_renderer = MinimapRenderer(self._screen, self._state, self._room_manager)
        self._ui_renderer = UIRenderer(self._screen, self._state)
        self._ui_renderer._map_renderer = self._map_renderer
        self._renderer = Renderer(self._screen, self._room_manager.world_bounds, self._ui_renderer)

        # инициализируем стартовое оружие
        self._state.weapon = Pointer(sprite=self._state.assets['pointer_sprite'],
                                     crosshair=self._state.assets['pointer_crosshair'])
        if self._state.player:
            self._state.player.weapon = self._state.weapon

        self._room_manager.update_active_room(self._state.player)

        # начальный спавн (2 bookworm в стартовой комнате)
        # if self._room_manager.active_room:
        #     enemies = self._spawner.spawn_in_room(self._room_manager.active_room, self._state)
        #     self._enemy_system.enemies.extend(enemies)
            # center = self._room_manager.start_room.bounds.center
            # spawn_area = pygame.Rect(center[0] - 120, center[1] - 120, 500, 300)
            # initial_enemies = []
            #
            # for _ in range(3):
            #     x = random.uniform(spawn_area.x + 52, spawn_area.right - 52)
            #     y = random.uniform(spawn_area.y + 52, spawn_area.bottom - 52)
            #     initial_enemies.append(self._spawner.spawn_bookworm(x, y))
            # self._enemy_system.enemies.extend(initial_enemies)


    def run(self) -> None:
        while self._state.is_running:
            # Delta time в секундах
            dt = self._clock.tick(config.FPS) / 1000.0

            is_ui_active = self._state.is_paused or self._state.is_minimap_visible
            pygame.mouse.set_visible(is_ui_active)

            events = pygame.event.get()

            if self._state.is_paused:
                self._ui_renderer.handle_input(events, self._state.weapon)
            else:
                self._input.process_events(events)

            if not self._state.is_paused:
                # hit-pause логика
                if self._hit_pause_frames > 0:
                    self._hit_pause_frames -= 1
                else:
                    dash_input = self._input.is_dash_requested()  # Отработка рывка
                    direction = self._input.get_move_direction()  # Вектор направления игрока

                    #  обновляем игрока
                    self._state.player.update(dx=direction[0], dy=direction[1], dt=dt, dash_requested=dash_input)

                    # Обновляем системы
                    self._state.projectile_system.update(dt, self._room_manager, self._state.enemy_system.enemies)
                    self._state.particle_system.update(dt)
                    self._state.enemy_system.update(dt, self._state, self._room_manager.active_room,
                                              self._renderer.debug_surface)
                    self._state.decals_system.update(dt)

                    # вычисляем координаты мыши для игрока
                    cam_off_x = self._camera.position.x - config.INTERNAL_WIDTH / 2
                    cam_off_y = self._camera.position.y - config.INTERNAL_HEIGHT / 2
                    mouse_screen = pygame.mouse.get_pos()
                    world_mouse = (mouse_screen[0] + cam_off_x, mouse_screen[1] + cam_off_y)
                    self._state.player.set_mouse_pos(world_mouse)


            # обновляем активную комнату
            new_room = self._room_manager.update_active_room(self._state.player)
            if self._room_manager.active_room != new_room:
                self._room_manager.prev_active_room = self._room_manager.active_room
                self._room_manager.active_room = new_room
                self._camera.start_transition(
                    self._room_manager.prev_active_room.bounds.center,
                    self._room_manager.active_room.bounds.center
                )
            self._room_manager.active_room.update_room_state(not bool(self._state.enemy_system.enemies))

            # респавним мобов при необходимости
            if self._room_manager.active_room.waves_count != 0 and not self._state.enemy_system.enemies:
                enemies = self._spawner.spawn_in_room(self._room_manager.active_room, self._state)
                self._state.enemy_system.enemies.extend(enemies)
                self._room_manager.active_room.waves_count -= 1

            # обновляем камеру
            self._camera.update(dt)

            # обновляем снаряды
            self._state.projectile_system.update(dt, self._room_manager, self._state.enemy_system.enemies)


            # обрабатываем коллизию со стенами
            if self._room_manager.active_room:
                self._collision_system.resolve_obstacles(self._state.player.body, self._room_manager.active_room.walls)

                for enemy in self._state.enemy_system.enemies:
                    self._collision_system.resolve_obstacles(enemy, self._room_manager.active_room.walls)

            # обрабатываем коллизию существ
            entities = self._state.enemy_system.enemies + [self._state.player]
            self._collision_system.resolve_movers(entities)

            # обработка стрельбы
            if self._state.weapon:
                shot_fired = self._weapon_system.update(dt, self._state.weapon, self._input.is_shooting_requested())
                if shot_fired:
                    self._state.weapon.fire(self._state.projectile_system, self._state)

            # отрисовка
            self._renderer.render(self._state, self._room_manager, self._camera)

            if self._input.spawn:
                cords = self._input.spawn_pos + self._room_manager.active_room.offset
                self._state.enemy_system.enemies.append(self._spawner.spawn_bookworm(*cords, 1.05 ** self._state.level_number))
                self._input.spawn = False

        pygame.quit()

    def _load_sprites(self, assets_manager: AssetManager) -> None:
        # Уровень
        self._state.level_seed = randint(1, 6)
        self._state.assets['wall_sprite'] = assets_manager.load_sprite(f"wall{self._state.level_seed}.png",
                                                 (config.TILE_SIZE, config.TILE_SIZE * 2))
        self._state.assets['floor_sprite'] = assets_manager.load_sprite(f"floor{self._state.level_seed}.png",
                                                  (config.TILE_SIZE, config.TILE_SIZE))

        self._state.assets['player_sprite'] = assets_manager.load_sprite("player.png",
                                                                         (config.PLAYER_SIZE,
                                                                          config.PLAYER_SIZE + 20))

        self._state.assets['pointer_sprite'] = assets_manager.load_sprite("pointer.png",
                                                                          (90, 60))
        self._state.assets['pointer_crosshair'] = assets_manager.load_sprite("pointer_crosshair.png",
                                                                             (20, 20))

        self._state.assets['hit_decal'] = assets_manager.load_sprite("splash.png",
                                                                     (75, 75))

    def _on_wall_impact(self, pos: tuple[float, float]) -> None:
        distance = Vector2((self._state.player.rect.centerx - pos[0],
                            self._state.player.rect.centery - pos[1])).magnitude()
        ratio = (1200 - distance) * 0.0015
        if ratio <= 0:
            ratio = 0

        self._state.particle_system.spawn_wall_impact(pos, color=config.MINIMAP_WALL_COLOR_LIST[self._state.level_seed - 1])
        self._camera.shake(config.IMPACT_SHAKE_AMOUNT * ratio, config.IMPACT_SHAKE_DURATION)

    def _on_enemy_impact(self, pos: tuple[float, float], enemy) -> None:
        self._state.particle_system.spawn_enemy_impact(pos, color=enemy.impact_color)

    def _on_player_impact(self, pos: tuple[float, float]) -> None:
        self._particle_system.spawn_wall_impact(pos, color=config.MINIMAP_WALL_COLOR_LIST[self._state.level_seed - 1])
        self._camera.shake(config.IMPACT_SHAKE_AMOUNT, config.IMPACT_SHAKE_DURATION)
        self._hit_pause_frames = config.IMPACT_HIT_PAUSE_FRAMES
