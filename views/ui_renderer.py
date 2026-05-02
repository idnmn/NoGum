import pygame
import config
from models.game_state import GameState
from models.player import Player
from views.map_renderer import MinimapRenderer


class UIRenderer:
    def __init__(self, screen: pygame.Surface, state: GameState) -> None:
        self._screen = screen
        self._state = state
        self._font = pygame.font.SysFont("Arial", 18, bold=True)
        self._map_renderer: MinimapRenderer = None

    def render_in_world(self, state: GameState, world_surface: pygame.Surface) -> None:
        self._draw_dash_indicator(state.player, world_surface)

    def render_out_world(self, state: GameState) -> None:
        self._draw_hp_bar(state.player)

        if self._state.is_minimap_visible:
            self._map_renderer.render()

    def _draw_hp_bar(self, player: Player) -> None:
        # фиксирован в левом верхнем углу
        x, y = 20, 20
        w, h = config.UI_HP_BAR_WIDTH, config.UI_HP_BAR_HEIGHT

        pygame.draw.rect(self._screen, config.UI_HP_BG_COLOR, (x, y, w, h))
        pygame.draw.rect(self._screen, config.UI_HP_COLOR, (x, y, int(w * player.hp_ratio), h))

        text_surf = self._font.render(f"{player.current_hp}/{player.max_hp}", True, config.UI_TEXT_COLOR)
        self._screen.blit(text_surf, (x + 10, y + 2))

    def _draw_dash_indicator(self, player: Player, world_surface: pygame.Surface) -> None:
        if not player.is_dash_ui_visible:
            return

        # рисуется на world_surface в мировых координатах
        center = player.body.rect.center
        bar_x = center[0] - config.UI_DASH_BAR_WIDTH / 2
        bar_y = center[1] + config.UI_DASH_OFFSET_Y

        pygame.draw.rect(world_surface, config.UI_DASH_BG_COLOR,
                         (bar_x, bar_y, config.UI_DASH_BAR_WIDTH, config.UI_DASH_BAR_HEIGHT))

        fill_w = int(config.UI_DASH_BAR_WIDTH * player.dash_cooldown_ratio)
        pygame.draw.rect(world_surface, config.UI_DASH_COLOR,
                         (bar_x, bar_y, fill_w, config.UI_DASH_BAR_HEIGHT))