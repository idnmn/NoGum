import pygame
import config
from pygame import Vector2
from models.game_state import GameState
from models.terminal import Terminal


# система терминалов
class TerminalSystem:
    def __init__(self, screen: pygame.Surface, state: GameState) -> None:
        self._state = state
        self._room_manager = state.room_manager
        self.terminals: list[Terminal] = self._room_manager.terminals
        self._new_selected = False

        # позиция по центру
        self._hud_rect = pygame.Rect(
            int((screen.get_width() - config.TERMINAL_HUD_WIDTH) / 2),
            int((screen.get_height() - config.TERMINAL_HUD_HEIGHT) / 2),
            config.TERMINAL_HUD_WIDTH,
            config.TERMINAL_HUD_HEIGHT
        )

        # основной слой для финального вывода (с альфа-каналом)
        self._layer = pygame.Surface(self._hud_rect.size, pygame.SRCALPHA)
        self._dark_layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self._dark_layer.fill((0, 0, 0))
        self._screen = screen

        # кэш для статичных элементов (комнаты + стены). Не перерисовывается каждый кадр
        self._static_cache: pygame.Surface | None = None

        self._scale: float = 1.0
        self._offset: tuple[float, float] = (0.0, 0.0)
        self._world_bounds: pygame.Rect = pygame.Rect(0, 0, 1, 1)
        self._walls_color = config.MINIMAP_WALL_COLOR_LIST[state.level_seed - 1]

        self._is_teleporting = False
        self.post_teleport_flag = False
        self._dark_timer = 0.0
        self._max_dark_time = config.TRANSITION_TIME

        self.set_world_bounds(self._room_manager.world_bounds)

    def resize(self) -> None:
        self._hud_rect = pygame.Rect(
            int((self._screen.get_width() - config.TERMINAL_HUD_WIDTH) / 2),
            int((self._screen.get_height() - config.TERMINAL_HUD_HEIGHT) / 2),
            config.TERMINAL_HUD_WIDTH,
            config.TERMINAL_HUD_HEIGHT
        )

        self._dark_layer = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        self._dark_layer.fill((0, 0, 0))

    # вычисляет масштаб и смещение для центрирования уровня на карте
    def set_world_bounds(self, bounds: pygame.Rect) -> None:
        self._world_bounds = bounds
        if bounds.width > 0 and bounds.height > 0:
            margin = 12
            self._scale = min(
                (self._hud_rect.width - margin) / bounds.width,
                (self._hud_rect.height - margin) / bounds.height
            )
            self._offset = (
                (self._hud_rect.width - bounds.width * self._scale) / 2,
                (self._hud_rect.height - bounds.height * self._scale) / 2
            )

    def update(self, dt: float) -> None:
        if self._is_teleporting:
            self._dark_timer -= dt

        if self._dark_timer < 0 and self._is_teleporting and not self.post_teleport_flag:
            self.post_teleport_flag = True
            self._state.player.current_tilt = 0
            self._dark_timer = self._max_dark_time
            self._state.audio_manager.play_sound('teleported', 2)

            # определяем терминал к которому телепортируемся
            selected_terminal = None
            for terminal in self.terminals:
                if terminal.is_selected:
                    selected_terminal = terminal
                    break

            # перемещаем игрока
            self._state.player.body.rect.x = selected_terminal.body.rect.x
            self._state.player.body.rect.y = selected_terminal.body.rect.y + config.TILE_SIZE
            self._state.player.body.vx = 0
            self._state.player.body.vy = 0

            # обновляем room manager и камеру
            self._room_manager.active_room = self._room_manager.update_active_room(self._state.player)

            room_center = self._room_manager.active_room.bounds.center

            self._state.camera.position = pygame.Vector2(room_center) + Vector2(0, -20)
            self._state.camera.curr_center = self._state.camera.position.copy() + Vector2(0, -20)
            self._state.camera.prev_center = self._state.camera.position.copy() + Vector2(0, -20)

        if self._dark_timer < 0 and self._is_teleporting and self.post_teleport_flag:
            self.post_teleport_flag = False
            self._is_teleporting = False
            self._state.is_terminal_ui_open = False
            self._state.is_paused = False
            self._state.audio_manager.crossfade_system.set_muted(False)

    # обособленный хэндлер
    def handle_input(self, events: list) -> None:
        if not self._is_teleporting:
            for event in events:
                if event.type == pygame.QUIT:
                    self._state.is_running = False

                # нажатия
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # выход из меню
                        self._state.is_terminal_ui_open = False
                        self._state.is_paused = False
                        self._state.audio_manager.crossfade_system.set_muted(False)
                        self._state.audio_manager.play_sound('terminal_close')

                # выделяем терминал, на который навелись мышью
                mouse_pos = pygame.mouse.get_pos()
                for terminal in [terminal for terminal in self.terminals if terminal.is_active]:
                    mw = terminal.body.rect.width
                    mh = terminal.body.rect.height
                    mx = (self._offset[0] + (terminal.body.rect.x - self._world_bounds.x) * self._scale - mw / 2
                          + self._hud_rect.x)
                    my = (self._offset[1] + (terminal.body.rect.y - self._world_bounds.y) * self._scale - mh / 2
                          + self._hud_rect.y)

                    rect = pygame.Rect(mx, my, mw * 2, mh * 2)

                    if rect.collidepoint(mouse_pos):
                        terminal.is_selected = True
                        self._new_selected = True
                        break
                    else:
                        terminal.is_selected = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for terminal in self.terminals:
                        if terminal.is_selected and not terminal.is_near_player:
                            self._is_teleporting = True
                            self._dark_timer = self._max_dark_time
                            self._state.stattracker.terminal_teleportations += 1

                        if terminal.is_near_player and not terminal.is_selected:
                            terminal.is_near_player = False

    def render(self) -> None:
        if not self.post_teleport_flag:
            self._screen.fill(config.BACKGROUND_COLOR)

        # рендерим статичную часть
        self._static_cache = pygame.Surface(self._hud_rect.size, pygame.SRCALPHA)
        self._static_cache.fill((0, 0, 0, 0))
        self._draw_static()

        # очищаем динамический слой
        self._layer.fill((0, 0, 0, 0))

        # Подложка и рамка интерфейса
        pygame.draw.rect(self._layer, config.MINIMAP_BG_COLOR, self._layer.get_rect(), border_radius=6)
        pygame.draw.rect(self._layer, config.MINIMAP_BORDER_COLOR, self._layer.get_rect(), 2, border_radius=6)

        # Накладываем кэш комнат и стен
        self._layer.blit(self._static_cache, (0, 0))

        # отрисовываем терминалы
        self._draw_layer()

        if not self.post_teleport_flag:
            # выводим на экран
            self._screen.blit(self._layer, self._hud_rect)

        # затемнение при телепортации
        if self._is_teleporting and not self.post_teleport_flag:
            ratio = min(255, int(255 * (1 - (self._dark_timer / (self._max_dark_time)) ** 3)))
            self._dark_layer.set_alpha(ratio)
            self._screen.blit(self._dark_layer, (0, 0))

        # высветление после телепортации
        elif self._is_teleporting and self.post_teleport_flag:
            ratio = min(255, int(255 * (self._dark_timer / (self._max_dark_time)) ** 3))
            self._dark_layer.set_alpha(ratio)
            self._screen.blit(self._dark_layer, (0, 0))

        pygame.display.flip()

    # отрисовка полов и стен. Выполняется редко, кэшируется
    def _draw_static(self) -> None:
        # Фоны комнат
        for room in self._state.room_manager.rooms:
            if room.is_explored or config.MINIMAP_EXPLORED:
                rx = self._offset[0] + (room.offset.x - self._world_bounds.x) * self._scale
                ry = self._offset[1] + (room.offset.y - self._world_bounds.y) * self._scale
                rw = room.bounds.width * self._scale
                rh = room.bounds.height * self._scale
                pygame.draw.rect(self._static_cache, config.MINIMAP_ROOM_BG_COLOR, (rx, ry, rw, rh))

                # стены (каждый тайл рисуется отдельно)
                for wall in room.walls:
                    mx = self._offset[0] + (wall.body.rect.x - self._world_bounds.x) * self._scale
                    my = self._offset[1] + (wall.body.rect.y - self._world_bounds.y) * self._scale
                    mw = wall.body.rect.width * self._scale
                    mh = wall.body.rect.height * self._scale
                    pygame.draw.rect(self._static_cache, self._walls_color, (mx, my, mw, mh))

                if room.exit:
                    exit = room.exit

                    mx = self._offset[0] + (exit.body.rect.x - self._world_bounds.x) * self._scale
                    my = self._offset[1] + (exit.body.rect.y - self._world_bounds.y) * self._scale
                    mw = exit.body.rect.width * self._scale
                    mh = exit.body.rect.height * self._scale
                    pygame.draw.rect(self._static_cache, config.EXIT_COLOR, (mx, my, mw, mh))

                if room.chest:
                    chest = room.chest

                    mx = self._offset[0] + (chest.body.rect.x - self._world_bounds.x) * self._scale
                    my = self._offset[1] + (chest.body.rect.y - self._world_bounds.y) * self._scale
                    mw = chest.body.rect.width * self._scale
                    mh = chest.body.rect.height * self._scale
                    pygame.draw.rect(self._static_cache, config.CHEST_COLOR, (mx, my, mw, mh))

    # Отрисовываем терминалы
    def _draw_layer(self):
        for terminal in [terminal for terminal in self.terminals if terminal.is_active]:
            if terminal.is_near_player or terminal.is_selected:  # терминал рядом с игроком
                scale = 0.8

            else:  # остальные терминалы
                scale = 0.6

            mw = terminal.body.rect.width * scale
            mh = terminal.body.rect.height * scale
            mx = self._offset[0] + (terminal.body.rect.x - self._world_bounds.x) * self._scale - mw / 2
            my = self._offset[1] + (terminal.body.rect.y - self._world_bounds.y) * self._scale - mh / 2

            if terminal.is_selected or terminal.is_near_player:
                source_sprite = terminal.near_player_sprite.copy()
            else:
                source_sprite = terminal.sprite_active.copy()
            sprite = pygame.transform.scale(source_sprite, (mw, mh))

            self._layer.blit(sprite, (mx, my))
