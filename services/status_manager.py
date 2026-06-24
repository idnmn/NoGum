import pygame
import configs.config
from models.game_state import GameState


class StatusManager:
    def __init__(self, state: GameState, owner):
        self._state = state
        self._owner = owner

        self.temperature = 0.0

        self.electrified = 0.0
        self._electrified_timer = 0.0
        self._electrified_decrease_time = 1.0

    def update(self, dt):
        self._electrified_timer -= dt
        if self.electrified > 100:
            self.electrified = 100

        slow_coef = (200 - self.electrified ) / 200
        self._owner.body.vx *= slow_coef
        self._owner.body.vy *= slow_coef

        # электричество
        if self.electrified:
            if self._electrified_timer < 0:
                self.electrified = max(0.0, self.electrified - 10)
                self._electrified_timer = self._electrified_decrease_time
                self._owner.take_damage(5, True)

            for _ in range(int(self.electrified) // 30 + 1):
                self._state.particle_system.spawn_electricity_marked(self._owner.rect.center,
                                                                     self._owner.rect.width)

    @property
    def status_list(self):
        heat, cold = 0, 0
        if self.temperature > 0.0:
            heat = self.temperature
            cold = 0.0
        elif self.temperature < 0.0:
            heat = 0.0
            cold = self.temperature

        status_list = [
            (self.electrified, configs.config.ELECTRICITY_COLOR),
            (heat, configs.config.HEAT_COLOR),
            (cold, configs.config.COLD_COLOR),
        ]
        return [status for status in status_list if status[0]]


