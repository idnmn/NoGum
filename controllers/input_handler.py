import pygame
import config
from models.game_state import GameState

# Обработчик входов
class InputHandler:
    def __init__(self, state: GameState) -> None:
        self._state = state
        self._dash_requested: bool = False
        self._shoot_requested = False
        self._reload_requested = False
        self._interactive_requested = False

        self.spawn = False
        self.spawn_pos = None

    # системные ивенты
    def process_events(self, events) -> None:
        self._dash_requested = False
        self._shoot_requested = False
        self._reload_requested = False
        self._interactive_requested = False

        for event in events:
            if event.type == pygame.QUIT:
                self._state.is_running = False
            # нажатия
            elif event.type == pygame.KEYDOWN:
                if not self._state.is_paused:
                    if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT): # Рывок
                        self._dash_requested = True

                    elif event.key == pygame.K_TAB: # миникарта
                        self._state.is_minimap_visible = True

                if event.key == pygame.K_ESCAPE and not self._state.is_upgrade_ui_open:
                    self._state.is_paused = not self._state.is_paused

                elif event.key == config.WEAPON_UI_KEY: # меню оружия
                    self._state.is_upgrade_ui_open = True
                    self._state.is_paused = True

                elif event.key == pygame.K_r and not self._state.is_paused:
                    self._reload_requested = True

                elif event.key == pygame.K_e and not self._state.is_paused:
                    self._interactive_requested = True


            # отжатия
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_TAB:  # миникарта
                    self._state.is_minimap_visible = False

            # нажатия мыши
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._shoot_requested = True
                self._state.weapon_fired = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._state.weapon_fired = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.spawn = True
                self.spawn_pos = event.pos

    def get_move_direction(self) -> tuple[float, float]:
        # возвращает сырой вектор ввода (-1, 0, 1) по осям X и Y
        if not self._state.is_paused:
            keys = pygame.key.get_pressed()
            dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
            dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
            return float(dx), float(dy)
        return 0.0, 0.0

    def is_dash_requested(self) -> bool: # проверяем отработку рывка
        return self._dash_requested

    def is_shooting_requested(self) -> bool:  # флаг выстрела
        if self._state.weapon.is_autofired:
            return self._shoot_requested or self._state.weapon_fired
        return self._shoot_requested

    def is_reload_requested(self) -> bool:  # проверка перезарядки
        return self._reload_requested

    def is_interactive_requested(self) -> bool: # проверка нажатия кнопки E для взаимодействия
        if self._interactive_requested:
            self._interactive_requested = False
            return True
        return False
