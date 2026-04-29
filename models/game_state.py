from dataclasses import dataclass, field

# Модели для всего
@dataclass
class GameState:
    is_running: bool = True
    player_pos_x: float = 400.0
    player_pos_y: float = 300.0
