import pygame
import config
from models.game_state import GameState
from models.player import Player
from models.weapons import *
from views.map_renderer import MinimapRenderer


class UIRenderer:
    def __init__(self, screen: pygame.Surface, state: GameState) -> None:
        self._screen = screen
        self._state = state
        self._font = pygame.font.Font("assets/QBF_font.ttf", 24)
        self._small_font = pygame.font.Font("assets/QBF_font.ttf", 20)
        self._title_font = pygame.font.Font("assets/QBF_font.ttf", 34)
        self._dragging_slider_label: str | None = None

        self._map_renderer: MinimapRenderer = None

    # единый расчёт геометрии панели
    def _get_panel_layout(self) -> dict:
        w, h = self._screen.get_size()
        panel_w, panel_h = 420, 550
        px = (w - panel_w) // 2
        py = (h - panel_h) // 2
        return {
            "px": px, "py": py, "panel_w": panel_w, "panel_h": panel_h,
            "start_y": py + 200, "gap": 60, "slider_w": panel_w - 40, "slider_h": 10
        }

    # данные для слайдеров
    def _get_slider_configs(self, weapon: Weapon) -> list[dict]:
        """
        единый источник правды для ползунков
        возвращает список объектов с полными данными для отрисовки и логики
        """
        layout = self._get_panel_layout()
        if type(weapon) == Pointer:
            return [
                {
                    "label": "Bullet Size",
                    "val": weapon.bullet_size,
                    "min": weapon.min_bullet_size,
                    "max": weapon.max_bullet_size,
                    "setter": weapon.change_size,
                    "rect": pygame.Rect(layout["px"] + 20, layout["start_y"], layout["slider_w"], layout["slider_h"])
                },
                {
                    "label": "Bullet Speed",
                    "val": weapon.bullet_speed,
                    "min": weapon.min_bullet_speed,
                    "max": weapon.max_bullet_speed,
                    "setter": weapon.change_speed,
                    "rect": pygame.Rect(layout["px"] + 20, layout["start_y"] + layout["gap"], layout["slider_w"],
                                        layout["slider_h"])
                },
                {
                    "label": "Fire Rate",
                    "val": weapon.fire_rate,
                    "min": weapon.min_fire_rate,
                    "max": weapon.max_fire_rate,
                    "setter": weapon.change_fire_rate,
                    "rect": pygame.Rect(layout["px"] + 20, layout["start_y"] + layout["gap"] * 2, layout["slider_w"],
                                        layout["slider_h"])
                }
            ]
        else:
            return []

    # внутренний обработчик действий пользователя внутри интерфейса
    def handle_input(self, events: list, weapon: Weapon | None) -> None:
        if not weapon:
            return

        configs = self._get_slider_configs(weapon)

        for event in events:
            if event.type == pygame.QUIT:
                self._state.is_running = False

            # нажатия
            elif event.type == pygame.KEYDOWN:
                if event.key == config.WEAPON_UI_KEY:  # выход из меню
                    self._state.is_upgrade_ui_open = False
                    self._state.is_paused = False

                elif event.key == pygame.K_ESCAPE and not self._state.is_upgrade_ui_open:
                    self._state.is_paused = not self._state.is_paused

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for cfg in configs:
                    if cfg["rect"].collidepoint(event.pos):
                        self._dragging_slider_label = cfg["label"]
                        self._apply_slider(cfg["label"], event.pos, weapon)
                        break
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._dragging_slider_label = None
            elif event.type == pygame.MOUSEMOTION and self._dragging_slider_label is not None:
                self._apply_slider(self._dragging_slider_label, event.pos, weapon)

    # изменение значений слайдеров
    def _apply_slider(self, label: str, pos: tuple[int, int], weapon: Weapon) -> None:
        """Строго линейное применение значения с округлением."""
        current_cfg = next((c for c in self._get_slider_configs(weapon) if c["label"] == label), None)
        if not current_cfg:
            return

        rect = current_cfg["rect"]
        mouse_x = max(rect.left, min(pos[0], rect.right))
        t = (mouse_x - rect.left) / rect.width
        raw_val = current_cfg["min"] + t * (current_cfg["max"] - current_cfg["min"])

        #  Округление значений перед применением
        if label == "Fire Rate":
            new_val = round(raw_val, 2)  # До десятых (0.1)
        else:
            new_val = round(raw_val, 1)     # До целых (1)

        current_cfg["setter"](new_val)

    # отрисовщик in-world составляющей
    def render_in_world(self, state: GameState, world_surface: pygame.Surface) -> None:
        self._draw_dash_indicator(state.player, world_surface)

    # отрисовщик out-world составляющкей
    def render_out_world(self, state: GameState) -> None:
        self._draw_hp_bar(state)

        if self._state.is_minimap_visible:
            self._map_renderer.render()

        self._draw_weapon_hud(state.weapon)

        # прицел виден только когда игра активна и нет открытых оверлеев
        if not state.is_paused and not state.is_minimap_visible:
            if state.weapon and state.weapon.crosshair:
                self._draw_crosshair(state.weapon.crosshair)

        if state.is_upgrade_ui_open:
            self._draw_upgrade_panel(state.weapon)

    # полоска хп игрока
    def _draw_hp_bar(self, state: GameState) -> None:
        # фиксирован в левом верхнем углу
        x, y = 20, 20
        h, w = config.UI_HP_BAR_HEIGHT, config.UI_HP_BAR_WIDTH

        # подложка
        bar_back = pygame.transform.scale(state.assets['hp_bar_back'], (w, h))
        # передник
        bar_top = pygame.transform.scale(state.assets['hp_bar_top'], (w, h))
        # заполнение
        bar_fill = pygame.transform.scale(state.assets['hp_bar_fill'],
                                          (int((307 / 558) * w * state.player.hp_ratio),
                                           int((121 / 200) * h)))
        fill_offset_x = int((225 / 558) * w)
        fill_offset_y = int((53 / 200) * h)

        self._screen.blit(bar_back, (x, y))
        self._screen.blit(bar_fill, (x + fill_offset_x, y + fill_offset_y))
        self._screen.blit(bar_top, (x, y))

        text_surf = self._font.render(f"{state.player.hp}/{state.player.max_hp}",
                                      True, config.UI_TEXT_COLOR)
        self._screen.blit(text_surf, (x + fill_offset_x,
                                      y + fill_offset_y + bar_fill.get_height() + 10))

    # индикатор зарядки рывка
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

    # худ для оружия
    def _draw_weapon_hud(self, weapon: Weapon | None) -> None:
        if not weapon or not weapon.name:
            return

        width, height = self._screen.get_size()

        surf = self._font.render(weapon.name, True, (255, 255, 255))
        surf_x = width - surf.get_width() - 20
        surf_y = height - surf.get_height() - 20

        # подложка
        hud_background = pygame.Surface((150, 120), pygame.SRCALPHA)
        hud_background.fill((30, 30, 30, 200))

        # спрайт оружия
        if not weapon.is_reloading:
            weapon_sprite = self._state.weapon.sprite
        else:
            weapon_sprite = self._state.weapon.reload_sprite
            weapon_sprite = pygame.transform.rotate(weapon_sprite, self._state.weapon.angle)
        weapon_sprite_x = hud_background.get_rect().x + 20
        weapon_sprite_y = hud_background.get_rect().y

        # индикатор обоймы
        indicator_sprite = pygame.transform.scale(self._state.assets["bullet_indicator"], (30, 30))
        indicator_sprite_x = hud_background.get_rect().x + 5
        indicator_sprite_y = hud_background.get_rect().y - 35
        clip = self._font.render(f"{weapon.clip}/{weapon.clip_size}", True, (255, 255, 255))
        clip_x = indicator_sprite.get_rect().right + 10
        clip_y = indicator_sprite.get_rect().y - 35


        self._screen.blit(hud_background, (width - 170, height - 140))
        self._screen.blit(weapon_sprite, (width - 170 + weapon_sprite_x, height - 100 + weapon_sprite_y))
        self._screen.blit(indicator_sprite, (width - 170 + indicator_sprite_x, height - 100 + indicator_sprite_y))
        self._screen.blit(surf, (surf_x, surf_y))
        self._screen.blit(clip, (width - 170 + clip_x, height - 100 + clip_y))

    # прицел
    def _draw_crosshair(self, sprite: pygame.Surface) -> None:
        pos = pygame.mouse.get_pos()
        ox = sprite.get_width() // 2
        oy = sprite.get_height() // 2
        self._screen.blit(sprite, (pos[0] - ox, pos[1] - oy))

    # панель настройки оружия
    def _draw_upgrade_panel(self, weapon: Weapon | None) -> None:
        layout = self._get_panel_layout()
        px, py, pw, ph = layout["px"], layout["py"], layout["panel_w"], layout["panel_h"]

        overlay = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self._screen.blit(overlay, (0, 0))

        pygame.draw.rect(self._screen, (25, 25, 35), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(self._screen, (60, 60, 85), (px, py, pw, ph), 2, border_radius=10)

        weapon_sprite = self._state.weapon.sprite

        self._screen.blit(self._title_font.render("Weapon Upgrade", True, (255, 255, 255)), (px + 20, py + 20))
        self._screen.blit(self._small_font.render(f"Model: {weapon.name}", True, (200, 200, 220)), (px + 20, py + 50))
        self._screen.blit(weapon_sprite, (px + 20, py + 80))

        #  отрисовка ползунков
        configs = self._get_slider_configs(weapon)

        for slider in configs:
            # текст значения
            self._screen.blit(self._small_font.render(f"{slider['label']}: {slider['val']:.2f}", True, (220, 220, 220)),
                              (slider["rect"].x, slider["rect"].y - 35))

            # подложка
            pygame.draw.rect(self._screen, (40, 40, 55), slider["rect"], border_radius=15)

            # линейный расчёт заполнения
            t = (slider["val"] - slider["min"]) / (slider["max"] - slider["min"])
            t = max(0.0, min(1.0, t))

            fill_w = int(slider["rect"].width * t)
            pygame.draw.rect(self._screen, (155, 255, 135),
                             (slider["rect"].x, slider["rect"].y, fill_w, slider["rect"].height),
                             border_radius=15)

            # ползунок
            knob_x = slider["rect"].x + int(slider["rect"].width * t)
            pygame.draw.rect(self._screen, (100, 100, 125), (knob_x - 9, slider["rect"].centery - 12, 19, 24))
            pygame.draw.rect(self._screen, (60, 60, 85), (knob_x - 7, slider["rect"].centery - 10, 15, 20))

        # статы
        stats_y = py + 340
        self._screen.blit(self._title_font.render("Stats:", True, (140, 140, 170)), (px + 20, stats_y))
        stats_y += 40

        texts = [
            ("Damage", f"{weapon.damage:.1f}"),
            ("Power", f"{weapon.power:.1f}"),
            ("Clip size", f"{weapon.clip_size}"),
            ("Reload time", f"{weapon.reload_cooldown:.1f}")
        ]

        for label, val in texts:
            self._screen.blit(self._small_font.render(f"{label}: {val}", True, (200, 200, 220)), (px + 20, stats_y))
            stats_y += 30

        self._screen.blit(self._small_font.render("Press I to close", True, (90, 90, 110)), (px + 20, py + ph - 35))