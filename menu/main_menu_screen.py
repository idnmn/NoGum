import pygame
import math
from collections.abc import Callable
from pygame import Vector2
from core import utils
import configs.config
from menu.screen import MenuScreen
from models.game_state import GameState
from ui_elements.button import MenuButton


# главное меню
class MainMenuScreen(MenuScreen):
    def __init__(self, state: GameState, screen_w: int, screen_h: int, start_game: Callable) -> None:
        super().__init__(state)

        self._background_art = pygame.transform.scale(state.assets['main_menu_art'], (screen_w, screen_h))

        self._title_char_list = [
            state.assets['n'],
            state.assets['o'],
            state.assets['g'],
            state.assets['u'],
            state.assets['m'],
            state.assets['!'],
        ]

        self._screen_w = screen_w
        self._screen_h = screen_h

        self._char_gap = 30
        self._title_width = (sum([char.get_width() for char in self._title_char_list]) +
                             self._char_gap * (len(self._title_char_list) - 1))
        self._title_start_x = (screen_w - self._title_width) / 2 + 30
        self._title_start_y = 80

        self._idle_par = 0
        self._idle_timer = 0

        self._button_start_y = 280
        self._button_start_x = 80
        self._button_gap = 40

        self.start_game = start_game
        self._start_game_button = MenuButton(
            title="Start Game",
            x=self._button_start_x,
            y=self._screen_h - self._button_start_y,
            width=0,
            height=35,
            is_active=True,
            action=start_game,
            uncentred=True
        )

        self._select_character_button = MenuButton(
            title="Select character",
            x=self._button_start_x,
            y=self._screen_h - self._button_start_y + self._button_gap,
            width=0,
            height=35,
            is_active=True,
            action=lambda: (setattr(self._state.menu_manager, 'active_screen', self._state.menu_screens['select_character']),
                            self._state.audio_manager.crossfade_system.set_muted(True)),
            uncentred=True
        )

        self._options_button = MenuButton(
            title="Options",
            x=self._button_start_x,
            y=self._screen_h - self._button_start_y + self._button_gap * 2,
            width=0,
            height=35,
            is_active=True,
            action=lambda: (setattr(self._state.menu_manager, 'active_screen', self._state.menu_screens['options']),
                            self._state.audio_manager.crossfade_system.set_muted(True),
                            self._state.menu_screens['options'].reinit()),
            uncentred=True
        )

        self._help_button = MenuButton(
            title="Help",
            x=self._button_start_x,
            y=self._screen_h - self._button_start_y + self._button_gap * 3,
            width=0,
            height=35,
            is_active=True,
            action=lambda: (setattr(self._state.menu_manager, 'active_screen', self._state.menu_screens['help']),
                            self._state.audio_manager.crossfade_system.set_muted(True)),
            uncentred=True
        )

        self._obituary_button = MenuButton(
            title="Obituary",
            x=self._button_start_x,
            y=self._screen_h - self._button_start_y + self._button_gap * 4,
            width=0,
            height=35,
            is_active=True,
            action=print,
            uncentred=True
        )

        self._exit_button = MenuButton(
            title="Exit",
            x=self._button_start_x,
            y=self._screen_h - self._button_start_y + self._button_gap * 5,
            width=0,
            height=35,
            is_active=True,
            action=lambda: setattr(self._state, 'is_running', False),
            uncentred=True
        )

        self._buttons = [self._start_game_button, self._select_character_button, self._options_button,
                         self._help_button, self._obituary_button, self._exit_button]
        self.ui_elements.extend(self._buttons)

    def update(self, dt: float, mouse_pos: Vector2, events: list[pygame.event.Event]) -> None:
        super().update(dt, mouse_pos, events)

        self._idle_timer -= dt

        if self._idle_timer < 0:
            self._idle_par -= 0.05
            self._idle_par %= 360
            self._idle_timer = 0.01

    def resize(self, width: int, height: int) -> None:
        self._screen_w = width
        self._screen_h = height

        self._background_art = pygame.transform.scale(self._state.assets['main_menu_art'], (width, height))
        self._title_start_x = (width - self._title_width) / 2

        # меняем положение элементов
        for i in range(len(self._buttons)):
            self._buttons[i].change_position(self._button_start_x,
                                             self._screen_h - self._button_start_y + self._button_gap * i)

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self._background_art, (0, 0))

        # отрисовываем название
        rendered_width = 0
        for i in range(len(self._title_char_list)):
            char = self._title_char_list[i]
            render_y = self._title_start_y + 20 * math.cos(self._idle_par + i * 0.5)
            screen.blit(char, (self._title_start_x + rendered_width, render_y))
            rendered_width += char.get_width() + self._char_gap

        font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 20)
        ver_title = font.render(configs.config.VERSION_TITLE, True, (50, 50, 50))
        x, y = self._screen_w - ver_title.get_width() - 10, self._screen_h - ver_title.get_height() - 10
        screen.blit(ver_title, (x, y))

        super().render(screen)