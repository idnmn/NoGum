import pygame
import config
from core import utils
from menu.screen import MenuScreen
from models.game_state import GameState
from ui_elements.button import MenuButton


class HelpWindow(MenuScreen):
    def __init__(self, state: GameState, screen_w: int, screen_h: int) -> None:
        super().__init__(state)

        self._background_art = pygame.transform.scale(state.assets['main_menu_art'], (screen_w, screen_h))

        self._screen_w = screen_w
        self._screen_h = screen_h

        self._text_start_y = 100
        self._text_gap = 40

        self._back_button = MenuButton(
            title="< Back",
            x=50,
            y=self._screen_h - 50,
            width=0,
            height=45,
            is_active=True,
            action=self._back,
            uncentred=True
        )

        self._keys_color = config.MENU_BUTTON_SELECTED_COLOR
        self._actions_color = config.MENU_BUTTON_ACTIVE_COLOR
        self._tips_font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 28)
        self._keys = [
            'W, A, S, D',
            'Right Shift',
            'LMB',
            'RMB',
            'I',
            'TAB',
            'E'
        ]
        self._actions = [
            ' - Передвижение',
            ' - Первый навык (рывок)',
            ' - Стрельба',
            ' - Второй навык (ближняя атака)',
            ' - Меню модификации оружия',
            ' - Миникарта',
            ' - Взаимодействие с объектами'
        ]

        self._buttons = [self._back_button]
        self.ui_elements.extend(self._buttons)

    def resize(self, width: int, height: int) -> None:
        self._screen_w = width
        self._screen_h = height

        self._background_art = pygame.transform.scale(self._state.assets['main_menu_art'], (width, height))

        self._back_button.change_position(50, self._screen_h - 50)

    def render(self, screen: pygame.Surface) -> None:
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((30, 30, 30, 220))
        screen.blit(self._background_art, (0, 0))
        screen.blit(background, (0, 0))

        title_font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 48)
        title = title_font.render("Help", True, (220, 220, 220))
        title_x = (self._screen_w - title.get_width()) // 2
        title_y = 30

        screen.blit(title, (title_x, title_y))

        for i, keys in enumerate(self._keys):
            keys_render = self._tips_font.render(keys, True, self._keys_color)
            y = self._text_start_y + self._text_gap * i
            x = 20

            screen.blit(keys_render, (x, y))

            tip_render = self._tips_font.render(self._actions[i], True, self._actions_color)
            x += keys_render.get_width()

            screen.blit(tip_render, (x, y))

        super().render(screen)

    def _back(self) -> None:
        self._state.audio_manager.crossfade_system.set_muted(False)
        self._state.menu_manager.set_active_screen(self._state.menu_screens['main_menu'])
