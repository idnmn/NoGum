import json
import datetime
from core import utils
from dataclasses import dataclass, asdict
from pathlib import Path

import pygame


@dataclass
class StatTracker:
    character: str = ''
    damage_dealt: int = 0
    damage_taken: int = 0
    kills: int = 0
    rooms_explored: int = 1
    levels_completed: int = 0
    terminal_teleportations: int = 0
    scrap_collected: int = 0
    inventory: dict[str: int] | None = None
    _date_time: str = None
    _play_time: float = 0.0

    @property
    def date_time(self) -> str:
        return datetime.datetime.now().strftime("%d%m%y_%H%M%S")

    @property
    def play_time(self) -> str:
        mins = int(self._play_time // 60)
        secs = int(self._play_time % 60)
        return f"{mins:02d}:{secs:02d}"

    # конвертирует все поля dataclass в словарь
    def to_dict(self) -> dict:
        return asdict(self)

    # создаёт объект из словаря
    @classmethod
    def from_dict(cls, data: dict) -> "StatTracker":
        known_fields = set(cls.__dataclass_fields__.keys())
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)

    # сохранение в json
    def save(self, filepath: str | Path) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    # загрузка из json
    @classmethod
    def load(cls, filepath: str | Path) -> "StatTracker":
        path = Path(filepath)
        if not path.exists():
            return cls()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except json.JSONDecodeError:
            print(f"ошибка чтения JSON: {path}")
            return cls()

    # сохраняет в runs/run_{id}.json
    def save_run(self, screenshot: pygame.Surface) -> None:
        path = Path("runs") / f"run_{self.date_time}.json"
        self.save(utils.get_resource_path(path))

        screenshots_dir = Path(utils.get_resource_path("runs")) / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = screenshots_dir / f"run_{self.date_time}_screenshot.png"
        pygame.image.save(screenshot, utils.get_resource_path(str(screenshot_path)))


    # загружает из runs/run_{id}.json
    @classmethod
    def load_run(cls, run_id: str | int) -> "StatTracker":
        return cls.load(Path("runs") / f"run_{run_id}.json")