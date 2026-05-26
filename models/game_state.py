from dataclasses import dataclass



# Модель игры
@dataclass
class GameState:
    # игровые данные
    level_seed: int = 1
    level_number: int = 0
    spawn_score: int = 3

    # флаги состояний
    is_running: bool = True

    is_minimap_visible: bool = False
    is_upgrade_ui_open: bool = False
    is_terminal_ui_open: bool = False
    is_paused: bool = False

    is_transition: bool = False # переход между этажами
    is_post_transition: bool = False

    # системы и объедки
    player = None
    weapon = None
    particle_system = None
    enemy_system = None
    decals_system = None
    projectile_system = None
    terminal_system = None
    assets = dict()
    camera = None
