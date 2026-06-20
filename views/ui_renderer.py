import config
from models.game_state import GameState
from skills.skill import Skill
from ui_elements.button import Button
from ui_elements.slider import Slider
from ui_elements.skill_hud_indicator import SkillIndicator
from models.weapons import *
from views.map_renderer import MinimapRenderer


class UIRenderer:
    def __init__(self, screen: pygame.Surface, state: GameState) -> None:
        self._screen = screen
        self._state = state
        self._font = pygame.font.Font("assets/QBF_font.ttf", 24)
        self._small_font = pygame.font.Font("assets/QBF_font.ttf", 20)
        self._title_font = pygame.font.Font("assets/QBF_font.ttf", 34)
        self._micro_font = pygame.font.Font("assets/QBF_font.ttf", 16)
        self._dragging_slider: Slider | None = None
        self._layout = self._get_panel_layout()

        self._map_renderer: MinimapRenderer | None = None

        # создаём слайдеры
        self._bullet_size_slider = Slider(
            title="Bullet Size",
            x=self._layout['px'] + 20,
            y=self._layout['start_y'],
            width=self._layout['slider_w'],
            max_value=self._state.weapon.max_bullet_size,
            min_value=self._state.weapon.min_bullet_size,
            round=1
        )

        self._bullet_speed_slider = Slider(
            title="Bullet Speed",
            x=self._layout['px'] + 20,
            y=self._layout['start_y'] + self._layout['gap'],
            width=self._layout['slider_w'],
            max_value=self._state.weapon.max_bullet_speed,
            min_value=self._state.weapon.min_bullet_speed,
            round=1
        )

        self._fire_rate_slider = Slider(
            title="Fire Rate",
            x=self._layout['px'] + 20,
            y=self._layout['start_y'] + self._layout['gap'] * 2,
            width=self._layout['slider_w'],
            max_value=self._state.weapon.max_fire_rate,
            min_value=self._state.weapon.min_fire_rate,
            round=1
        )

        self._sliders = [
            (self._bullet_size_slider, self._state.weapon.change_size),
            (self._bullet_speed_slider, self._state.weapon.change_speed),
            (self._fire_rate_slider, self._state.weapon.change_fire_rate),
        ]

        # кнопка прокачки оружия
        self.upgrade_button = Button(
            title="Upgrade",
            x=self._layout['px'] + 240,
            y=self._layout['start_y'] + self._layout['gap'] * 2 + 40,
            width=150,
            height=45,
            is_active=True,
            action=self._upgrade_weapon
        )
        self._state.buttons.append(self.upgrade_button)

        # индикаторы скилов
        self.first_skill_indicator = SkillIndicator(
            x=self._screen.get_width() / 4 - 50,
            y=self._screen.get_height() - 80,
            skill=self._state.player.first_skill
        )

        self.second_skill_indicator = SkillIndicator(
            x=self._screen.get_width() / 4 + 50,
            y=self._screen.get_height() - 80,
            skill=self._state.player.second_skill
        )

    def _upgrade_weapon(self):
        weapon = self._state.weapon
        self._state.player.scrap -= weapon.upgrade_cost
        weapon.upgrade()

        self._bullet_size_slider.max_value = weapon.max_bullet_size
        self._bullet_speed_slider.max_value = weapon.max_bullet_speed
        self._fire_rate_slider.max_value = weapon.max_fire_rate

    # единый расчёт геометрии панели
    def _get_panel_layout(self) -> dict:
        w, h = self._screen.get_size()
        panel_w, panel_h = 420, 550
        px = (w - panel_w) // 2
        py = (h - panel_h) // 2
        return {
            "px": px, "py": py, "panel_w": panel_w, "panel_h": panel_h,
            "start_y": py + 180, "gap": 60, "slider_w": panel_w - 40, "slider_h": 10
        }

    # внутренний обработчик действий пользователя внутри интерфейса
    def handle_input(self, events: list) -> None:
        weapon = self._state.weapon
        if not weapon:
            return

        for event in events:
            if event.type == pygame.QUIT:
                self._state.is_running = False

            # нажатия
            elif event.type == pygame.KEYDOWN:
                if event.key == config.WEAPON_UI_KEY or event.key == pygame.K_ESCAPE:  # выход из меню
                    self._state.is_upgrade_ui_open = False
                    self._state.is_paused = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for item in self._sliders:
                    slider = item[0]
                    seter = item[1]

                    if slider.interactive_hitbox.collidepoint(event.pos):
                        slider.handle_click(event.pos)
                        seter(slider.value)
                        self._dragging_slider = item
                        break

                if (self.upgrade_button.interactive_hitbox.collidepoint(event.pos)
                        and self.upgrade_button.is_active):
                    self.upgrade_button.click()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self._dragging_slider = None
            elif event.type == pygame.MOUSEMOTION and self._dragging_slider:
                self._dragging_slider[0].handle_click(event.pos)
                self._dragging_slider[1](self._dragging_slider[0].value)

    # балансируем значения слайдеров
    def _balance_slider_value(self) -> None:
        weapon = self._state.weapon

        self._sliders[0][0].value = weapon.bullet_size
        self._sliders[1][0].value = weapon.bullet_speed
        self._sliders[2][0].value = weapon.fire_rate

    # отрисовщик in-world составляющей
    def render_in_world(self, world_surface: pygame.Surface) -> None:
        self._draw_skill_indicator(world_surface, self._state.player.first_skill, 1)
        self._draw_skill_indicator(world_surface, self._state.player.second_skill, 2)

    # отрисовщик out-world составляющкей
    def render_out_world(self) -> None:
        state = self._state

        self._draw_hp_bar()

        self._draw_scrap_counter()

        self._draw_inventory()

        self.first_skill_indicator.render(self._screen)
        self.second_skill_indicator.render(self._screen)

        if self._state.is_minimap_visible:
            self._map_renderer.render()

        self._draw_weapon_hud()

        # прицел виден только когда игра активна и нет открытых оверлеев
        if not state.is_paused and not state.is_minimap_visible:
            if state.weapon and state.weapon.crosshair:
                self._draw_crosshair(state.weapon.crosshair)

        if state.is_upgrade_ui_open:
            self._draw_upgrade_panel()

        if config.PRINT_FPS:
            self._draw_fps_counter()

    # полоска хп игрока
    def _draw_hp_bar(self) -> None:
        state = self._state

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

    # счетчик обломков
    def _draw_scrap_counter(self) -> None:
        state = self._state

        # фиксирован в левом верхнем углу
        x, y = 30, 100

        self._screen.blit(state.assets['scrap_ico'], (x, y))

        text_surf = self._font.render(f"{state.player.scrap}",
                                      True, config.UI_TEXT_COLOR)
        self._screen.blit(text_surf, (x + 40, y + 8))

    # индикатор зарядки скилла
    def _draw_skill_indicator(self, world_surface: pygame.Surface, skill: Skill, skill_number: int) -> None:
        if skill.is_ready:
            return

        background_color = skill.indicator_background_color
        fill_color = skill.indicator_fill_color

        player = self._state.player

        # рисуется на world_surface в мировых координатах
        bar_offset_y = config.UI_SKILL_BAR_HEIGHT + 2 if skill_number == 2 else 0

        center = player.body.rect.center
        bar_x = center[0] - config.UI_SKILL_BAR_WIDTH / 2
        bar_y = center[1] + config.UI_SKILL_OFFSET_Y + bar_offset_y

        pygame.draw.rect(world_surface, background_color,
                         (bar_x, bar_y, config.UI_SKILL_BAR_WIDTH, config.UI_SKILL_BAR_HEIGHT))

        fill_w = int(config.UI_SKILL_BAR_WIDTH * skill.cooldown_ratio)
        pygame.draw.rect(world_surface, fill_color,
                         (bar_x, bar_y, fill_w, config.UI_SKILL_BAR_HEIGHT))

    # худ для оружия
    def _draw_weapon_hud(self) -> None:
        weapon = self._state.weapon

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

    # худ для собранных предметов
    def _draw_inventory(self) -> None:
        start_y = self._screen.get_height() - 300
        start_x = 20

        # подложка
        hud_background = pygame.Surface((70, 285), pygame.SRCALPHA)
        hud_background.fill((30, 30, 30, 120))

        self._screen.blit(hud_background, (start_x, start_y - 10))

        for i, item in enumerate(self._state.drop_pool):
            # спрайт
            w, h = self._state.assets[item[1]].get_size()
            sprite = pygame.transform.scale(self._state.assets[item[1]], (w * 0.7, h * 0.7))
            self._screen.blit(sprite, (start_x + 10, start_y + (60 * i)))

            # количество
            counter = self._font.render(f"{self._state.player.inventory[item[1].capitalize()][0]}",
                                          True, config.UI_TEXT_COLOR)
            self._screen.blit(counter, (start_x + 40, start_y + (60 * i)))

    # счетчик FPS
    def _draw_fps_counter(self) -> None:
        x = self._screen.get_width() - 40
        y = 5

        pygame.draw.rect(self._screen, (30, 30, 30), (x, y, 35, 20))

        fps = int(self._state.clock.get_fps())
        if fps < 50:
            color = (255, 60, 60)
        elif fps < 80:
            color = (255, 125, 75)
        elif fps < 120:
            color = (255, 245, 140)
        else:
            color = (110, 255, 60)
        self._screen.blit(self._micro_font.render(str(fps), True, color), (x + 1, y + 1))

    # прицел
    def _draw_crosshair(self, sprite: pygame.Surface) -> None:
        pos = pygame.mouse.get_pos()
        ox = sprite.get_width() // 2
        oy = sprite.get_height() // 2
        self._screen.blit(sprite, (pos[0] - ox, pos[1] - oy))

    # панель настройки оружия
    def _draw_upgrade_panel(self) -> None:
        weapon = self._state.weapon
        self._balance_slider_value() # балансируем слайдеры

        self.upgrade_button.is_active = (self._state.player.scrap >= weapon.upgrade_cost) # обновляем состояние кнопки

        layout = self._get_panel_layout()
        px, py, pw, ph = layout["px"], layout["py"], layout["panel_w"], layout["panel_h"]

        overlay = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self._screen.blit(overlay, (0, 0))

        pygame.draw.rect(self._screen, (25, 25, 35), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(self._screen, (60, 60, 85), (px, py, pw, ph), 2, border_radius=10)

        weapon_sprite = self._state.weapon.sprite

        self._screen.blit(self._title_font.render("Weapon Upgrade", True,
                                                  (255, 255, 255)), (px + 20, py + 20))
        self._screen.blit(self._small_font.render(f"Model: {weapon.name}", True,
                                                  (200, 200, 220)), (px + 20, py + 50))
        self._screen.blit(self._small_font.render(f"LvL: {weapon.level}", True,
                                                  (200, 200, 220)), (px + 250, py + 50))
        self._screen.blit(weapon_sprite, (px + 20, py + 80))

        #  отрисовка ползунков
        for slider in [item[0] for item in self._sliders]:
            slider.render(self._screen)

        # отрисовываем кнопку
        self.upgrade_button.render(self._screen)

        button_x, button_y = self.upgrade_button.x, self.upgrade_button.y
        self._screen.blit(self._state.assets["scrap_ico"], (button_x, button_y + 50))

        cost_color = (220, 220, 220) if self._state.player.scrap >= weapon.upgrade_cost else (255, 100, 100)
        self._screen.blit(self._small_font.render(f" X {weapon.upgrade_cost}", True,
                                                  cost_color), (button_x + 30, button_y + 57))

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

    # изменения элементов при масштабировании окна
    def resize(self) -> None:
        # меняем положение индикаторов скиллов
        self.first_skill_indicator.x = self._screen.get_width() / 4 - 50
        self.first_skill_indicator.y = self._screen.get_height() - 80

        self.second_skill_indicator.x = self._screen.get_width() / 4 + 50
        self.second_skill_indicator.y = self._screen.get_height() - 80

        # пересчитываем лайаут
        self._layout = self._get_panel_layout()

        # сдвигаем кнопки и слайдеры
        self._bullet_size_slider.change_position(self._layout['px'] + 20,
                                                 self._layout['start_y'])
        self._bullet_speed_slider.change_position(self._layout['px'] + 20,
                                                  self._layout['start_y'] + self._layout['gap'])
        self._fire_rate_slider.change_position(self._layout['px'] + 20,
                                                  self._layout['start_y'] + self._layout['gap'] * 2)

        self.upgrade_button.change_position(self._layout['px'] + 240,
                                            self._layout['start_y'] + self._layout['gap'] * 2 + 40)


