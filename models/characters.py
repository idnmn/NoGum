from models.game_state import GameState
from models.player import Player


class Slasher(Player):
    def __init__(self, x: float, y: float, state: GameState) -> None:
        super().__init__(x, y, state, 'slasher')
        self.signature_color = (100, 230, 175)


class Electron(Player):
    def __init__(self, x: float, y: float, state: GameState) -> None:
        super().__init__(x, y, state, 'electron')
        self.signature_color = (155, 240, 255)


class Tank(Player):
    def __init__(self, x: float, y: float, state: GameState) -> None:
        super().__init__(x, y, state, 'tank')
        self.signature_color = (235, 175, 0)
