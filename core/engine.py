import pygame
import config
from models.game_state import GameState
from controllers.input_handler import InputHandler
from models.player import Player
from models.room_manager import RoomManager
from models.camera import Camera
from services.collision import CollisionSystem
from views.renderer import Renderer

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

        # инициализируем игру и объекты
        self._state = GameState()

        # инициализируем подземелье ДО игрока, чтобы взять координаты спавна
        self._room_manager = RoomManager()
        self._room_manager._generate_grid()
        spawn_center = self._room_manager.active_room.bounds.center

        self._state.player = Player(
            x=spawn_center[0] - config.PLAYER_SIZE / 2,
            y=spawn_center[1] - config.PLAYER_SIZE / 2
        )

        # инструменты и сервисы
        self._clock = pygame.time.Clock()
        self._input = InputHandler(self._state)
        self._renderer = Renderer(self._screen, self._room_manager.world_bounds)
        self._collision_system = CollisionSystem()

        self._room_manager.update_active_room(self._state.player)

        self._camera = Camera()
        self._camera.position = pygame.Vector2(spawn_center)
        self._camera.curr_center = self._camera.position.copy()
        self._camera.prev_center = self._camera.position.copy()

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