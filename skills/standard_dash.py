from pygame import Vector2
import config
from models.game_state import GameState
from skills.skill import Skill


# стандартный рывок
class StandardDash(Skill):
    def __init__(self, state: GameState) -> None:
        super().__init__(state)

        self.speed = config.STANDARD_DASH_SPEED
        self._cool_down = config.STANDARD_DASH_COOLDOWN
        self.duration = config.STANDARD_DASH_DURATION
        self._ui_timer: float = 0.0

        # фиксируем направление игрока в начале рывка
        self.dx = 0.0
        self.dy = 0.0

        # констранты для рендера индикатора
        self.indicator_background_color = config.UI_DASH_BG_COLOR
        self.indicator_fill_color = config.UI_DASH_COLOR
        self.indicator_sprite = self._state.assets['dash_ico']


    def update(self, dt: float) -> None:
        super().update(dt)

        if self.is_using:
            self._state.particle_system.spawn_while_dash(self._state.player.rect.center, Vector2(self._state.player.body.dx,
                                                                                           self._state.player.body.dy),
                                                         config.UI_DASH_COLOR, config.PLAYER_SIZE)
            # фиксируем направление игрока
            self._state.player.body.dx, self._state.player.body.dy = self.dx, self.dy

    def reload(self) -> None:
        super().reload()
        self._state.particle_system.spawn_dash_reloaded(self._state.player.rect.center)

    def ended(self) -> None:
        super().ended()

        # сбрасываем ускорение
        self._state.player.acceleration //= 100
        self._state.player.current_max_speed = self._state.player.max_speed
        self._state.player.ignore_enemy = False

    def use(self, mouse_pos: Vector2) -> None:
        if self._state.player.body.dx != 0 or self._state.player.body.dy != 0:
            self.dx, self.dy = Vector2(self._state.player.body.ax, self._state.player.body.ay).normalize()
            super().use(mouse_pos)

            self._use_timer = self.duration

            self._state.particle_system.spawn_dashed(self._state.player.rect.center)

            # ускоряем игрока
            self._state.player.acceleration *= 100
            self._state.player.current_max_speed = self.speed
            self._state.player.ignore_enemy = True

            self._state.audio_manager.play_sound('dash')



