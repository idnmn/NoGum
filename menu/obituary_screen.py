import os
import pygame
import random
from core import utils
from pygame import Vector2
from menu.screen import MenuScreen
from models.game_state import GameState
from ui_elements.button import MenuButton
from ui_elements.run_card import RunCard


class ObituaryScreen(MenuScreen):
    def __init__(self, state: GameState, screen_w: int, screen_h: int) -> None:
        super().__init__(state)

        self._background_art = pygame.transform.scale(state.assets['main_menu_art'], (screen_w, screen_h))

        self._screen_w = screen_w
        self._screen_h = screen_h

        self._text_start_y = 100
        self._text_gap = 40

        path = utils.get_resource_path("runs")
        if not os.path.exists(path):
            os.makedirs(path)
        self._runs_list = [file for file in os.listdir(path) if file.endswith(".json")]
        self._current_run_index = 0

        self._back_button = MenuButton(
            title="< Back",
            x=20,
            y=self._screen_h - 50,
            width=0,
            height=45,
            is_active=True,
            action=self._back,
            uncentred=True
        )

        self._next_run_button = MenuButton(
            title="Next >",
            x=self._screen_w - 160,
            y=(self._screen_h - 45) // 2,
            width=0,
            height=45,
            is_active=True,
            action=lambda: setattr(self._state.menu_manager.active_screen, 'current_run_index',
                                   self.current_run_index + 1)
        )

        self._prev_run_button = MenuButton(
            title="< Prev",
            x=20,
            y=(self._screen_h - 45) // 2,
            width=0,
            height=45,
            is_active=True,
            action=lambda: setattr(self._state.menu_manager.active_screen, 'current_run_index',
                                   self.current_run_index - 1),
        )

        self._start_button = MenuButton(
            title="Start >",
            x=self._screen_w - 170,
            y=self._screen_h - 50,
            width=0,
            height=45,
            is_active=True,
            uncentred=True,
            action=lambda: (setattr(self._state, "character", self._run_cards[self._current_run_index].data['character']),
                            self._state.engine._start_game(),
                            self._state.audio_manager.crossfade_system.set_muted(False),
                            self._state.audio_manager.crossfade_system.stop(),
                            self._state.audio_manager.play_music(random.choice(
                                self._state.audio_manager.crossfade_system._music_list)),)
        )

        self._run_cards = []
        for run in list(self._runs_list)[::-1]:
            self._run_cards.append(RunCard(state, run, screen_w, screen_h))

        self._buttons = [self._back_button, self._prev_run_button, self._next_run_button, self._start_button]
        self.ui_elements.extend(self._buttons)

    def reinit(self) -> None:
        path = utils.get_resource_path("runs")
        if not os.path.exists(path):
            os.makedirs(path)
        self._runs_list = [file for file in os.listdir(path) if file.endswith(".json")]
        self._current_run_index = 0
        self._run_cards.clear()
        for run in list(self._runs_list)[::-1]:
            self._run_cards.append(RunCard(self._state, run, self._screen_w, self._screen_h))

    @property
    def current_run_index(self) -> int:
        return self._current_run_index

    @current_run_index.setter
    def current_run_index(self, value):
        if self._run_cards:
            self._current_run_index = max(0, value % len(self._runs_list))

    def resize(self, width: int, height: int) -> None:
        self._screen_w = width
        self._screen_h = height

        self._background_art = pygame.transform.scale(self._state.assets['main_menu_art'], (width, height))

        self._back_button.change_position(20, self._screen_h - 50)
        self._prev_run_button.change_position(20, (self._screen_h - 45) // 2)
        self._next_run_button.change_position(self._screen_w - 160, (self._screen_h - 45) // 2)
        self._start_button.change_position(self._screen_w - 350, self._screen_h - 50)

        for card in self._run_cards:
            card.resize(width, height)

    def update(self, dt: float, mouse_pos: Vector2, events: list[pygame.event.Event]):
        super().update(dt, mouse_pos, events)

        if self._run_cards:
            self._run_cards[self._current_run_index].update(dt, mouse_pos, events)

    def render(self, screen: pygame.Surface) -> None:
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((30, 30, 30, 220))
        screen.blit(self._background_art, (0, 0))
        screen.blit(background, (0, 0))

        if self._run_cards:
            self._run_cards[self._current_run_index].render(screen)

        super().render(screen)

    def _back(self) -> None:
        self._state.audio_manager.crossfade_system.set_muted(False)
        self._state.menu_manager.set_active_screen(self._state.menu_screens['main_menu'])

    def _handle_events(self, events: list[pygame.event.Event]) -> None:
        super()._handle_events(events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self._next_run_button.click()

                if event.key == pygame.K_a:
                    self._prev_run_button.click()

                if event.key == pygame.K_RETURN:
                    self._start_button.click()
