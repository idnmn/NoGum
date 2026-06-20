from models.game_state import GameState
from menu.screen import MenuScreen


class MenuManager:
    def __init__(self, state: GameState):
        self._state = state

        self.active_screen = None

    def set_active_screen(self, screen: MenuScreen) -> None:
        self.active_screen = screen