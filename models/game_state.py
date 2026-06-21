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
    in_game: bool = False

    weapon_fired: bool = False

    is_minimap_visible: bool = False
    is_upgrade_ui_open: bool = False
    is_terminal_ui_open: bool = False
    is_paused: bool = False

    is_transition: bool = False # переход между этажами
    is_post_transition: bool = False

    hit_pause_frames: int = 0

    # системы и объедки
    player = None
    weapon = None
    clock = None
    room_manager = None
    particle_system = None
    enemy_system = None
    decals_system = None
    projectile_system = None
    collectable_system = None
    collision_system = None
    terminal_system = None
    buttons = []
    resizable_elements = []
    assets = dict()
    camera = None
    stattracker = None
    menu_manager = None
    menu_screens = dict()

    # дроп пул
    drop_pool = None

    # системные величины
    master_volume: int = 100
    ui_volume: int = 100
    music_volume: int = 100

    def reset_state(self) -> None:
        self.is_running: bool = True
        self.in_game: bool = False

        self.weapon_fired: bool = False

        self.is_minimap_visible: bool = False
        self.is_upgrade_ui_open: bool = False
        self.is_terminal_ui_open: bool = False
        self.is_paused: bool = False

        self.is_transition: bool = False  # переход между этажами
        self.is_post_transition: bool = False
