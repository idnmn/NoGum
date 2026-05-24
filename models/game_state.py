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
    weapon: Weapon | None = None
    level_number: int = 0
    spawn_score: int = 3

    # флаги состояний
    is_upgrade_ui_open: bool = False
    is_terminal_ui_open: bool = False

    # системы
    particle_system = None
    enemy_system = None
    decals_system = None
    projectile_system = None
    terminal_system = None
    assets = dict()
    camera = None
