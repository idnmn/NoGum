from dataclasses import dataclass
from models.player import Player
from models.weapons import Weapon

# Модель игры
@dataclass
class GameState:
    is_running: bool = True
    player: Player | None = None
    is_minimap_visible: bool = False
    level_seed: int = 1
    is_paused: bool = False
    is_upgrade_ui_open: bool = False
    weapon: Weapon | None = None