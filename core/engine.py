import pygame
import config
from core.asset_manager import AssetManager
from models.game_state import GameState
from controllers.input_handler import InputHandler
from models.player import Player
from models.room_manager import RoomManager
from models.camera import Camera
from services.collision import CollisionSystem
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

        # грузим спрайты
        assets_manager = AssetManager()
        wall_sprite = assets_manager.load_sprite("wall.png", (config.TILE_SIZE, config.TILE_SIZE*2))
        floor_sprite = assets_manager.load_sprite("floor1.png", (config.TILE_SIZE, config.TILE_SIZE))
        player_sprite = assets_manager.load_sprite("player.png", (config.PLAYER_SIZE,
                                                                                        config.PLAYER_SIZE+20))

        # инициализируем игру и объекты
        self._state = GameState()

        # инициализируем подземелье ДО игрока, чтобы взять координаты спавна
        self._room_manager = RoomManager(wall_sprite=wall_sprite, floor_sprite=floor_sprite)
        spawn_center = self._room_manager.active_room.bounds.center

        # инструменты и сервисы
        self._clock = pygame.time.Clock()
        self._input = InputHandler(self._state)
        self._collision_system = CollisionSystem()

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
                sprite=player_sprite
            )

            # kамера тоже стартует с центра стартовой комнаты
            self._camera.position = pygame.Vector2(spawn_center)
            self._camera.curr_center = self._camera.position.copy()
            self._camera.prev_center = self._camera.position.copy()
        else:
            # Fallback на случай ошибки генерации
            self._state.player = Player(config.INTERNAL_WIDTH / 2, config.INTERNAL_HEIGHT / 2, player_sprite)
            self._camera.position = pygame.Vector2(config.INTERNAL_WIDTH / 2, config.INTERNAL_HEIGHT / 2)
            self._camera.curr_center = self._camera.position.copy()
            self._camera.prev_center = self._camera.position.copy()

        # рендереры
        self._map_renderer = MinimapRenderer(self._screen, self._state.player, self._room_manager)
        self._ui_renderer = UIRenderer(self._screen, self._state)
        self._ui_renderer._map_renderer = self._map_renderer
        self._renderer = Renderer(self._screen, self._room_manager.world_bounds, self._ui_renderer)

        self._room_manager.update_active_room(self._state.player)


    def run(self) -> None:
        while self._state.is_running:
            # Delta time в секундах
            dt = self._clock.tick(config.FPS) / 1000.0

            self._input.process_events()
            dash_input = self._input.is_dash_requested() # Отработка рывка
            direction = self._input.get_move_direction() # Вектор направления игрока


            # обновляем игрока
            self._state.player.update(dx=direction[0], dy=direction[1], dt=dt, dash_requested=dash_input)

            # обновляем активную комнату
            new_room = self._room_manager.update_active_room(self._state.player)
            if self._room_manager.active_room != new_room:
                self._room_manager.prev_active_room = self._room_manager.active_room
                self._room_manager.active_room = new_room
                self._camera.start_transition(
                    self._room_manager.prev_active_room.bounds.center,
                    self._room_manager.active_room.bounds.center
                )

            # обновляем камеру
            self._camera.update(dt)

            # обрабатываем коллизию со стенами
            if self._room_manager.active_room:
                self._collision_system.resolve(self._state.player, self._room_manager.active_room.walls)

            self._renderer.render(self._state, self._room_manager, self._camera)

            # print(self._room_manager.active_room.bounds.center, self._camera.position, self._state.player.body.center, sep='\n')

        pygame.quit()