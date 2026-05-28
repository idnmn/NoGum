from dataclasses import dataclass


# статтрекер для игрока
@dataclass
class StatTracker:
    damage_dealt: int = 0
    damage_taken: int = 0
    kills: int = 0

    rooms_explored: int = 1
    levels_completed: int = 0
    terminal_teleportations: int = 0

    scrap_collected: int = 0
