from dataclasses import dataclass
from models.player import Player

# Модель игры
@dataclass
class GameState:
    is_running: bool = True
    player: Player | None = None