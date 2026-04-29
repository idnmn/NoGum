import pygame
import config
from models.game_state import GameState
from controllers.input_handler import InputHandler
from models.player import Player
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

        self._clock = pygame.time.Clock()
        self._state = GameState()
        self._state.player = Player()
        self._input = InputHandler(self._state)
        self._renderer = Renderer(self._screen)

    def run(self) -> None:
        while self._state.is_running:
            # Delta time в секундах
            dt = self._clock.tick(config.FPS) / 1000.0

            self._input.process_events()
            dash_input = self._input.is_dash_requested() # Отработка рывка
            direction = self._input.get_move_direction() # Вектор направления игрока


            # Обновляем позицию
            self._state.player.update(
                dx=direction[0],
                dy=direction[1],
                dt=dt,
                acceleration=config.PLAYER_ACCELERATION,
                friction=config.PLAYER_FRICTION,
                max_speed=config.PLAYER_MAX_SPEED,
                dash_speed=config.PLAYER_DASH_SPEED,
                dash_duration=config.PLAYER_DASH_DURATION,
                dash_cooldown=config.PLAYER_DASH_COOLDOWN,
                dash_requested=dash_input
            )

            self._renderer.render(self._state)

        pygame.quit()