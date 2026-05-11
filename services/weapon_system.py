import pygame
from models.weapons import Weapon

# управляет стрельбой
class WeaponSystem:
    def __init__(self) -> None:
        self._fire_cooldown_timer: float = 0.0

    def update(self, dt: float, weapon: Weapon, is_shooting_requested: bool, is_reload_requested: bool) -> bool:
        """
        Обновляет таймер кулдауна и возвращает True, если выстрел был произведён.
        dt - Delta time в секундах
        weapon - Текущее оружие (содержит fire_rate)
        is_shooting_requested - Флаг нажатия кнопки стрельбы
        if_reload_requested - флаг нажатия кнопки перезарядки
        return True, если выстрел состоялся
        """
        # обновляем таймеры
        if self._fire_cooldown_timer > 0:
            self._fire_cooldown_timer -= dt

        if weapon.reload_timer > 0:
            weapon.reload_timer -= dt

        # пробуем выстрелить если есть флаг от input_handler
        if is_shooting_requested and self._fire_cooldown_timer <= 0 and weapon.clip > 0:
            self._fire_cooldown_timer = 1.0 / weapon.fire_rate
            weapon.clip -= 1
            return True

        # усли кончились патроны в обойме или прожата кнопка перезарядки перезаряжаемся
        if (((weapon.clip == 0 and is_shooting_requested) or
             (is_reload_requested and weapon.clip != weapon.clip_size))
                and not weapon.is_reloading):
            weapon.is_reloading = True
            weapon.reload_timer = weapon.reload_cooldown

        if weapon.reload_timer <= 0 and weapon.is_reloading:
            weapon.is_reloading = False
            weapon.clip = weapon.clip_size

        return False
