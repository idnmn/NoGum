import pygame
from pygame import Vector2
from menu.screen import MenuScreen
from models.game_state import GameState
from ui_elements.button import MenuButton
from ui_elements.character_card import CharacterCard


class SelectCharacter(MenuScreen):
    def __init__(self, state: GameState, screen_w: int, screen_h: int) -> None:
        super().__init__(state)

        self._background_art = pygame.transform.scale(state.assets['main_menu_art'], (screen_w, screen_h))

        self._screen_w = screen_w
        self._screen_h = screen_h

        self._text_start_y = 100
        self._text_gap = 40

        self._current_character_index = 0

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

        self._next_character_button = MenuButton(
            title="Next >",
            x=self._screen_w - 160,
            y=(self._screen_h - 45) // 2,
            width=0,
            height=45,
            is_active=True,
            action=lambda: setattr(self._state.menu_manager.active_screen, 'current_character_index',
                                   self.current_character_index + 1)
        )

        self._prev_character_button = MenuButton(
            title="< Prev",
            x=20,
            y=(self._screen_h - 45) // 2,
            width=0,
            height=45,
            is_active=True,
            action=lambda: setattr(self._state.menu_manager.active_screen, 'current_character_index',
                                   self.current_character_index - 1),
        )

        self._character_cards = []
        for character in list(self._state.character_pool.keys()):
            self._character_cards.append(CharacterCard(state, character, screen_w, screen_h))

        self._buttons = [self._back_button, self._prev_character_button, self._next_character_button]
        self.ui_elements.extend(self._buttons)

    @property
    def current_character(self) -> int:
        return list(self._state.character_pool.keys())[self._current_character_index]

    @property
    def current_character_index(self) -> int:
        return self._current_character_index

    @current_character_index.setter
    def current_character_index(self, value):
        self._current_character_index = max(0, value % len(self._state.character_pool))

    def resize(self, width: int, height: int) -> None:
        self._screen_w = width
        self._screen_h = height

        self._background_art = pygame.transform.scale(self._state.assets['main_menu_art'], (width, height))

        self._back_button.change_position(20, self._screen_h - 50)
        self._prev_character_button.change_position(20, (self._screen_h - 45) // 2)
        self._next_character_button.change_position(self._screen_w - 160, (self._screen_h - 45) // 2)

        for card in self._character_cards:
            card.resize(width, height)

    def update(self, dt: float, mouse_pos: Vector2, events: list[pygame.event.Event]):
        super().update(dt, mouse_pos, events)

        self._character_cards[self._current_character_index].update(dt, mouse_pos, events)

    def render(self, screen: pygame.Surface) -> None:
        background = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        background.fill((30, 30, 30, 220))
        screen.blit(self._background_art, (0, 0))
        screen.blit(background, (0, 0))

        self._character_cards[self._current_character_index].render(screen)

        super().render(screen)

    def _back(self) -> None:
        self._state.audio_manager.crossfade_system.set_muted(False)
        self._state.menu_manager.set_active_screen(self._state.menu_screens['main_menu'])

    def _handle_events(self, events: list[pygame.event.Event]) -> None:
        super()._handle_events(events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    self._next_character_button.click()

                if event.key == pygame.K_a:
                    self._prev_character_button.click()

                if event.key == pygame.K_RETURN:
                    self._character_cards[self._current_character_index].start_button.click()
