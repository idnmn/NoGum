import pygame
from models.game_state import GameState

# Обработчик входов
class InputHandler:
    def __init__(self, state: GameState) -> None:
        self._state = state

    def process_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._state.is_running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key)

    def _handle_key_press(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            self._state.is_running = False
