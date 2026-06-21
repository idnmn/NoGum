import pygame
from pygame import Vector2

from menu.screen import MenuScreen
from models.game_state import GameState
from ui_elements.button import MenuButton, Button
from ui_elements.slider import Slider


class PauseScreen(MenuScreen):
    def __init__(self, state: GameState, screen_w: int, screen_h: int) -> None:
        super().__init__(state)

        self._screen_w = screen_w
        self._screen_h = screen_h

        self._button_start_y = 140
        self._button_gap = 60

        self._slider_w = 300

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

        self._back_to_menu_button = MenuButton(
            title="Back to Menu",
            x=(self._screen_w - self._slider_w) // 2,
            y=self._button_start_y + self._button_gap * 3,
            width=0,
            height=30,
            is_active=True,
            action=lambda: setattr(self._state.menu_manager.active_screen, '_exit_dialogue_active', True),
            uncentred=False
        )

        self._sliders = [self._volume_slider, self._sound_volume_slider, self._music_volume_slider]

        self._buttons = [self._back_to_menu_button]

        self.ui_elements.extend(self._sliders)
        self.ui_elements.extend(self._buttons)

        self._exit_dialogue_active = False
        self._exit_dialogue_w = 400
        self._exit_dialogue_h = 200
        self._exit_dialogue_x = (self._screen_w - self._exit_dialogue_w) // 2
        self._exit_dialogue_y = (self._screen_h - self._exit_dialogue_h) // 2

        self._confirm_exit_button = Button(
            title="Exit",
            x=self._exit_dialogue_x + 220,
            y=self._exit_dialogue_y + 130,
            width=150,
            height=45,
            is_active=True,
            action=self._exit_to_menu
        )

        self._cancel_exit_button = Button(
            title="Cancel",
            x=self._exit_dialogue_x + 30,
            y=self._exit_dialogue_y + 130,
            width=150,
            height=45,
            is_active=True,
            action=lambda: setattr(self._state.menu_manager.active_screen, '_exit_dialogue_active', False)
        )

        self._dialogue_ui_elements = [self._confirm_exit_button, self._cancel_exit_button]

    def update(self, dt: float, mouse_pos: Vector2, events: list[pygame.event.Event]) -> None:
        if not self._exit_dialogue_active:
            super().update(dt, mouse_pos, events)
        else:
            for element in self._dialogue_ui_elements:
                element.update(dt, mouse_pos)

            for event in events:
                if event.type == pygame.QUIT:
                    self._state.is_running = False
                # нажатия кнопок
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self._dialogue_ui_elements:
                        if button.state == 'selected':
                            button.click()
                            break

    def resize(self, width: int, height: int) -> None:
        self._screen_w = width
        self._screen_h = height

        # меняем положение элементов
        for i, element in enumerate(self.ui_elements):
            self.ui_elements[i].change_position((self._screen_w - element.width) // 2,
                                             self._button_start_y + self._button_gap * i)

        self._exit_dialogue_x = (self._screen_w - self._exit_dialogue_w) // 2
        self._exit_dialogue_y = (self._screen_h - self._exit_dialogue_h) // 2
        self._cancel_exit_button.change_position(self._exit_dialogue_x + 30, self._exit_dialogue_y + 130)
        self._confirm_exit_button.change_position(self._exit_dialogue_x + 220, self._exit_dialogue_y + 130)

    def render(self, screen: pygame.Surface) -> None:
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((30, 30, 30, 220))
        screen.blit(background, (0, 0))

        font = pygame.font.Font("assets/QBF_font.ttf", 48)
        title = font.render("Pause", True, (220, 220, 220))
        title_x = (self._screen_w - title.get_width()) // 2
        title_y = 50

        screen.blit(title, (title_x, title_y))

        super().render(screen)

        if self._exit_dialogue_active:
            w, h = self._exit_dialogue_w, self._exit_dialogue_h
            x = self._exit_dialogue_x
            y = self._exit_dialogue_y
            pygame.draw.rect(screen, (25, 25, 35), (x + 2, y + 2, w - 4, h - 4), border_radius=10)
            pygame.draw.rect(screen, (60, 60, 85), (x, y, w, h), 2, border_radius=10)

            # предупреждение
            text1 = 'ВНИМАНИЕ!'
            text2 = 'При выходе данные забега'
            text2_2 = 'не сохранятся.'
            text3 = 'Всё равно выйти?'
            font1 = pygame.font.Font("assets/QBF_font.ttf", 32)
            font2 = pygame.font.Font("assets/QBF_font.ttf", 24)
            attension_msg_1 = font1.render(text1, True, (255, 100, 100))
            attension_msg_2 = font2.render(text2, True, (220, 220, 220))
            attension_msg_2_2 = font2.render(text2_2, True, (220, 220, 220))
            attension_msg_3 = font1.render(text3, True, (220, 220, 220))
            screen.blit(attension_msg_1, (x + 120, y + 15))
            screen.blit(attension_msg_2, (x + 20, y + 40))
            screen.blit(attension_msg_2_2, (x + 20, y + 60))
            screen.blit(attension_msg_3, (x + 20, y + 80))


            for element in self._dialogue_ui_elements:
                element.render(screen)

    def _exit_to_menu(self):
        self._state.in_game = False
        self._state.menu_manager.set_active_screen(self._state.menu_screens['main_menu'])

        self._exit_dialogue_active = False

