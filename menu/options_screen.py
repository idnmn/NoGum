import pygame

from menu.screen import MenuScreen
from models.game_state import GameState
from ui_elements.button import MenuButton
from ui_elements.slider import Slider


class OptionsScreen(MenuScreen):
    def __init__(self, state: GameState, screen_w: int, screen_h: int) -> None:
        super().__init__(state)

        self._background_art = pygame.transform.scale(state.assets['main_menu_art'], (screen_w, screen_h))

        self._screen_w = screen_w
        self._screen_h = screen_h

        self._button_start_y = 240
        self._button_gap = 80

        self._slider_w = 400

        self._volume_slider = Slider(
            title="Master Volume",
            x=(self._screen_w - self._slider_w) // 2,
            y=self._button_start_y,
            width=self._slider_w,
            max_value=100,
            min_value=0,
            default_value=self._state.audio_manager.master_volume * 100,
            round=0,
            stepped=True,
            step=5,
            setter=self._state.audio_manager.set_master_volume,
        )

        self._sound_volume_slider = Slider(
            title="Sounds Volume",
            x=(self._screen_w - self._slider_w) // 2,
            y=self._button_start_y + self._button_gap,
            width=self._slider_w,
            max_value=100,
            min_value=0,
            default_value=self._state.audio_manager.sound_volume * 100,
            round=0,
            stepped=True,
            step=5,
            setter=self._state.audio_manager.set_sound_volume,
        )

        self._music_volume_slider = Slider(
            title="Music Volume",
            x=(self._screen_w - self._slider_w) // 2,
            y=self._button_start_y + self._button_gap * 2,
            width=self._slider_w,
            max_value=100,
            min_value=0,
            default_value=self._state.audio_manager.music_volume * 100,
            round=0,
            stepped=True,
            step=5,
            setter=self._state.audio_manager.set_music_volume,
        )

        self._sliders = [self._volume_slider, self._sound_volume_slider, self._music_volume_slider]

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

        self._buttons = [self._back_button]
        self.ui_elements.extend(self._sliders)
        self.ui_elements.extend(self._buttons)

    def resize(self, width: int, height: int) -> None:
        self._screen_w = width
        self._screen_h = height

        self._background_art = pygame.transform.scale(self._state.assets['main_menu_art'], (width, height))

        # меняем положение элементов
        for i, element in enumerate(self.ui_elements):
            self.ui_elements[i].change_position((self._screen_w - element.width) // 2,
                                             self._button_start_y + self._button_gap * i)

        self._back_button.change_position(50, self._screen_h - 50)

    def render(self, screen: pygame.Surface) -> None:
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((30, 30, 30, 220))
        screen.blit(self._background_art, (0, 0))
        screen.blit(background, (0, 0))

        font = pygame.font.Font("assets/QBF_font.ttf", 48)
        title = font.render("Options", True, (220, 220, 220))
        title_x = (self._screen_w - title.get_width()) // 2
        title_y = 150

        screen.blit(title, (title_x, title_y))

        super().render(screen)

    def _back(self) -> None:
        self._state.audio_manager.crossfade_system.set_muted(False)
        self._state.menu_manager.set_active_screen(self._state.menu_screens['main_menu'])
