import pygame
from models.game_state import GameState

# Обработчик входов
class InputHandler:
    def __init__(self, state: GameState) -> None:
        self._state = state
        self._dash_requested: bool = False

    # системные ивенты
    def process_events(self) -> None:
        self._dash_requested = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._state.is_running = False
            # нажатия
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._state.is_running = False

                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT): # Рывок
                    self._dash_requested = True

                elif event.key == pygame.K_TAB: # миникарта
                    self._state.is_minimap_visible = True

            # отжатия
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_TAB:  # миникарта
                    self._state.is_minimap_visible = False

    def get_move_direction(self) -> tuple[float, float]:
        # возвращает сырой вектор ввода (-1, 0, 1) по осям X и Y
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        return float(dx), float(dy)

    def is_dash_requested(self) -> bool: # проверяем отработку рывка
        return self._dash_requested
