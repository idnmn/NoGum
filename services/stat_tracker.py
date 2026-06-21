import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class StatTracker:
    damage_dealt: int = 0
    damage_taken: int = 0
    kills: int = 0
    rooms_explored: int = 1
    levels_completed: int = 0
    terminal_teleportations: int = 0
    scrap_collected: int = 0
    inventory: dict[str: int] | None = None
    _time: float = 0.0

    @property
    def time(self) -> str:
        mins = int(self._time // 60)
        secs = int(self._time % 60)
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
    def save_run(self, run_id: str | int) -> None:
        path = Path("runs") / f"run_{run_id}.json"
        self.save(path)

    # загружает из runs/run_{id}.json
    @classmethod
    def load_run(cls, run_id: str | int) -> "StatTracker":
        return cls.load(Path("runs") / f"run_{run_id}.json")