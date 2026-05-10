import pygame
from models.weapons import Weapon

# управляет стрельбой
class WeaponSystem:
    def __init__(self) -> None:
        self._fire_cooldown_timer: float = 0.0

    def update(self, dt: float, weapon: Weapon, is_shooting_requested: bool) -> bool:
        """
        Обновляет таймер кулдауна и возвращает True, если выстрел был произведён.
        dt - Delta time в секундах
        weapon - Текущее оружие (содержит fire_rate)
        s_shooting_requested - Флаг нажатия кнопки стрельбы
        return True, если выстрел состоялся
        """
        if self._fire_cooldown_timer > 0:
            self._fire_cooldown_timer -= dt

        if is_shooting_requested and self._fire_cooldown_timer <= 0:
            self._fire_cooldown_timer = 1.0 / weapon.fire_rate
            return True
        return False
