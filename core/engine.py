from random import randint
from core import utils
from core.asset_manager import AssetManager
from controllers.input_handler import InputHandler
from core.audio_manager import AudioManager
from menu.help_window import HelpWindow
from menu.ingame_pause_screen import PauseScreen
from menu.main_menu_screen import MainMenuScreen
from menu.menu_manager import MenuManager
from menu.options_screen import OptionsScreen
from services.room_manager import RoomManager
from models.camera import Camera
from models.weapons import *
from models.collectable import *
from models.characters import *
from services.collectable_system import CollectableSystem
from services.collision_system import CollisionSystem
from services.decal_system import DecalSystem
from services.enemy_system import EnemySystem
from services.spawner import Spawner
from services.stat_tracker import StatTracker
from services.terminal_system import TerminalSystem
from services.weapon_system import WeaponSystem
from services.projectile_system import ProjectileSystem
from services.particle_system import ParticleSystem
from skills.skills import StandardDash, Slash
from views.renderer import Renderer
from views.ui_renderer import UIRenderer
from views.map_renderer import MinimapRenderer

# Основной движок
class GameEngine:
    def __init__(self) -> None:
        pygame.init()

        # настройки окна
        self.min_window_width = 1000
        self.min_window_height = 600
        self.last_win_w = 0
        self.last_win_h = 0
        self.target_aspect = config.INTERNAL_WIDTH / config.INTERNAL_HEIGHT
        self.is_fullscreen = False

        # инициализируем игру
        self._state = GameState()
        self._renderer = None
        self._state.clock = pygame.time.Clock()
        self._state.audio_manager = AudioManager(self._state)
        self._state.audio_manager.play_music('astra')
        pygame.mixer.set_num_channels(16)

        # Инициализация окна
        self._screen = pygame.display.set_mode(
            (config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT),
            pygame.RESIZABLE
        )
        self._fx_layer = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)

        pygame.display.set_caption(config.WINDOW_TITLE)

        # иконка
        icon = pygame.image.load(utils.get_resource_path('assets/icon.ico'))
        pygame.display.set_icon(icon)

        # внутренний таймер перехода между сценами
        self._transition_timer = config.TRANSITION_TIME

        # ГРУЗИМ СПРАЙТЫ
        self._assets_manager = AssetManager()
        self._load_sprites(self._assets_manager)

        # меню
        self._state.menu_manager = MenuManager(self._state)
        menu_screens = {
            'main_menu': MainMenuScreen(self._state, *self._screen.get_size(), self._start_game),
            'options': OptionsScreen(self._state, *self._screen.get_size()),
            'help': HelpWindow(self._state, *self._screen.get_size()),
            'pause': PauseScreen(self._state, *self._screen.get_size())
        }
        self._state.menu_screens = menu_screens

        # заполняем пулы
        self._state.skills_pool = {
            'standart_dash': StandardDash,
            'slash': Slash,
        }
        self._state.character_pool = {
            'slasher': Slasher,
            'electron': Electron,
            'tank': Tank
        }
        self._state.weapon_pool = {
            'pointer': Pointer,
            'tazer': Tazer,
            'bulldog': Bulldog
        }

        self._state.menu_manager.set_active_screen(menu_screens['main_menu'])

    def run(self) -> None:
        while self._state.is_running:
            # Delta time в секундах
            dt = self._state.clock.tick(config.FPS) / 1000.0
            if self._state.audio_manager.crossfade_system:
                self._state.audio_manager.crossfade_system.update(dt)

            events = pygame.event.get()

            is_ui_active = (self._state.is_paused or self._state.is_minimap_visible) or not self._state.in_game
            pygame.mouse.set_visible(is_ui_active)

            # обработка изменения размера
            for event in events:
                if event.type == pygame.VIDEORESIZE and ((event.w != self.last_win_w) or (event.h != self.last_win_h)):
                    if event.w != self.last_win_w:
                        self._constrain_window(event.w, event.h, True)
                    elif event.h != self.last_win_h:
                        self._constrain_window(event.w, event.h, False)

                    self.last_win_h = event.h
                    self.last_win_w = event.w

                    for element in self._state.resizable_elements:
                        element.resize()

                # переключение полноэкранного режима (F11)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self._toggle_fullscreen()

            # Переход между уровнями
            if self._state.is_transition:
                self._transition_timer -= dt
                # затемнение и осветление экрана
                if not self._state.is_post_transition:
                    ratio = min(255, int(255 * (1 - (self._transition_timer / (config.TRANSITION_TIME)) ** 3)))
                else:
                    ratio = min(255, int(255 * ((self._transition_timer / (config.TRANSITION_TIME)) ** 3)))

                self._renderer.fx_surface.fill((0, 0, 0))
                self._renderer.fx_surface.set_alpha(ratio)

                if self._transition_timer < 0 and not self._state.is_post_transition:
                    if self._state.in_game:
                        self._goto_new_level()
                    else:
                        self._state.in_game = True
                    self._state.is_post_transition = True
                    self._state.is_paused = False
                    self._transition_timer = config.TRANSITION_TIME
                    self._state.audio_manager.play_sound('teleported', 1.7)

                if self._transition_timer < 0 and self._state.is_post_transition:
                    self._state.is_transition = False
                    self._state.is_post_transition = False
                    self._state.audio_manager.crossfade_system.set_muted(False)

            # ИГРОВОЙ ЦИКЛ
            if self._state.in_game:
                # заглушка дроппула
                if not self._state.drop_pool:
                    print('clear')
                    self._state.drop_pool = [(Nothing, 'nothing')]

                # перераспределяем хэндлеры
                if self._state.is_upgrade_ui_open:
                    self._ui_renderer.handle_input(events)
                elif self._state.is_terminal_ui_open:
                    self._state.terminal_system.handle_input(events)
                else:
                    self._input.process_events(events)

                # обновляем кнопки
                if self._state.buttons and self._state.is_paused:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self._state.buttons:
                        button.update(dt, mouse_pos, self._state)

                # не на паузе
                if not self._state.is_paused:
                    self._state.stattracker._play_time += dt

                    # hit-pause логика
                    if self._state.hit_pause_frames > 0:
                        self._state.hit_pause_frames -= 1
                    else:
                        direction = self._input.get_move_direction()  # Вектор направления игрока

                        # обновляем игрока
                        self._state.player.update(dx=direction[0], dy=direction[1], dt=dt)

                        # общий список сущностей
                        entities = ([enemy.body for enemy in self._state.enemy_system.enemies] +
                                    [self._state.player.body])
                        if self._state.room_manager.active_room.terminal:
                            entities.append(self._state.room_manager.active_room.terminal.body)
                        if self._state.room_manager.active_room.chest:
                            entities.append(self._state.room_manager.active_room.chest.body)

                        # обновляем интерактивные объекты в комнате
                        self._state.room_manager.update_interactives(self._state, dt)

                        # Обновляем системы
                        self._state.projectile_system.update(dt, self._state.enemy_system.enemies)
                        self._state.particle_system.update(dt)
                        self._state.collectable_system.update(dt)
                        self._state.enemy_system.update(dt, self._state, self._renderer.debug_surface)
                        self._state.decals_system.update(dt)
                        self._state.decals_system.update_shadows(entities)

                        # вычисляем координаты мыши для игрока
                        win_w, win_h = self._screen.get_size()
                        int_w, int_h = config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT

                        # коэффициент масштабирования окна относительно внутренней поверхности игры
                        scale_x = win_w / int_w
                        scale_y = win_h / int_h

                        mouse_screen = pygame.mouse.get_pos()

                        # переводим курсор из оконных координат во внутренние
                        mouse_int_x = mouse_screen[0] / scale_x
                        mouse_int_y = mouse_screen[1] / scale_y

                        # смещение камеры относительно внутреннего центра
                        cam_off_x = self._state.camera.position.x - int_w / 2
                        cam_off_y = self._state.camera.position.y - int_h / 2

                        # итоговые мировые координаты
                        world_mouse = (mouse_int_x + cam_off_x, mouse_int_y + cam_off_y)
                        self._state.player.set_mouse_pos(world_mouse)

                        # обновляем активную комнату
                        new_room = self._state.room_manager.update_active_room(self._state.player)
                        if self._state.room_manager.active_room != new_room:
                            self._state.room_manager.prev_active_room = self._state.room_manager.active_room
                            self._state.room_manager.active_room = new_room
                            self._state.camera.start_transition(
                                self._state.room_manager.prev_active_room.bounds.center + Vector2(0, -20),
                                self._state.room_manager.active_room.bounds.center + Vector2(0, -20)
                            )
                        self._state.room_manager.active_room.update_room_state(not bool(self._state.enemy_system.enemies),
                                                                         self._state.camera, self._state)

                        # респавним мобов при необходимости
                        if self._state.room_manager.active_room.waves_count != 0 and not self._state.enemy_system.enemies:
                            enemies = self._spawner.spawn_in_room(self._state.room_manager.active_room, self._state)
                            self._state.enemy_system.enemies.extend(enemies)
                            self._state.room_manager.active_room.waves_count -= 1

                        # обновляем камеру
                        self._state.camera.update(dt)

                        # обновляем снаряды
                        self._state.projectile_system.update(dt, self._state.enemy_system.enemies)

                        # обрабатываем коллизию со стенами и терминалами
                        if self._state.room_manager.active_room:
                            self._state.collision_system.resolve_obstacles(self._state.player.body,
                                                                     self._state.room_manager.active_room.walls)
                            if self._state.room_manager.active_room.terminal:
                                self._state.collision_system.resolve_obstacles(self._state.player.body,
                                                                        [self._state.room_manager.active_room.terminal.body])
                            if self._state.room_manager.active_room.exit:
                                self._state.collision_system.resolve_obstacles(self._state.player.body,
                                                                        [self._state.room_manager.active_room.exit.body])
                            if self._state.room_manager.active_room.chest:
                                self._state.collision_system.resolve_obstacles(self._state.player.body,
                                                                        [self._state.room_manager.active_room.chest.body])

                            for enemy in self._state.enemy_system.enemies:
                                self._state.collision_system.resolve_obstacles(enemy, self._state.room_manager.active_room.walls)
                                if self._state.room_manager.active_room.terminal:
                                    self._state.collision_system.resolve_obstacles(enemy,
                                                                            [self._state.room_manager.active_room.terminal.body])

                        # обрабатываем коллизию существ
                        self._state.collision_system.resolve_movers(entities)

                        # обработка стрельбы и перезарядки
                        if self._state.weapon:
                            shot_fired = self._weapon_system.update(dt, self._input.is_shooting_requested(),
                                                                    self._input.is_reload_requested())
                            if shot_fired:
                                self._state.weapon.fire()

                        # обработка скиллов
                        if self._input.is_first_skill_used() and self._state.player.first_skill.is_ready:
                            self._state.player.first_skill.use(pygame.mouse.get_pos())

                        if self._input.is_second_skill_used() and self._state.player.second_skill.is_ready:
                            self._state.player.second_skill.use(pygame.mouse.get_pos())

                        # проверяем взаимодействие с объектами
                        if self._input.is_interactive_requested():

                            # взаимодействие с терминалом
                            if self._state.room_manager.active_room.terminal and not self._state.is_terminal_ui_open:
                                terminal = self._state.room_manager.active_room.terminal
                                if terminal.is_near_player and terminal.is_active:
                                    self._state.is_paused = True
                                    self._state.is_terminal_ui_open = True
                                    self._state.is_upgrade_ui_open = False
                                    self._state.is_minimap_visible = False

                                    self._state.audio_manager.crossfade_system.set_muted(True)
                                    self._state.audio_manager.play_sound('terminal_open')

                            # взаимодействие с выходом
                            if (self._state.room_manager.active_room.exit and
                                    self._state.room_manager.active_room.exit.is_near_player):
                                if self._state.room_manager.active_room.terminal:
                                    if not self._state.is_terminal_ui_open:
                                        self._state.is_transition = True
                                        self._state.is_paused = True

                                        self._state.audio_manager.crossfade_system.set_muted(True)

                                        self._transition_timer = config.TRANSITION_TIME
                                else:
                                    self._state.is_transition = True
                                    self._state.is_paused = True

                                    self._state.audio_manager.crossfade_system.set_muted(True)

                                    self._transition_timer = config.TRANSITION_TIME

                            # открытие сундука
                            if (self._state.room_manager.active_room.chest and
                                self._state.room_manager.active_room.chest.is_closed):
                                if self._state.room_manager.active_room.terminal:
                                    if not self._state.is_terminal_ui_open:
                                        self._state.room_manager.active_room.chest.open(self._state)
                                else:
                                    self._state.room_manager.active_room.chest.open(self._state)

                # на паузе
                else:
                    if self._state.is_terminal_ui_open:
                        self._state.terminal_system.update(dt)

                # отрисовка (раскидываем рендереры)
                # при post_tp вызываем оба рендерера
                # открытая пауза
                if (not (self._state.is_upgrade_ui_open or self._state.is_terminal_ui_open or self._state.is_transition)
                        and self._state.is_paused):
                    self._renderer.render(False) # не обновляет кадр
                    self._state.menu_manager.active_screen.update(dt, pygame.mouse.get_pos(), events)
                    self._state.menu_manager.active_screen.render(self._screen)
                    pygame.display.flip()
                elif self._state.is_terminal_ui_open and self._state.terminal_system.post_teleport_flag:
                    # общий список сущностей
                    entities = ([enemy.body for enemy in self._state.enemy_system.enemies] +
                                [self._state.player.body])
                    if self._state.room_manager.active_room.terminal:
                        entities.append(self._state.room_manager.active_room.terminal.body)
                    if self._state.room_manager.active_room.chest:
                        entities.append(self._state.room_manager.active_room.chest.body)

                    self._state.decals_system.update_shadows(entities)

                    self._renderer.render(False) # не обновляет кадр
                    self._state.terminal_system.render()

                # вне post_tp рендерим только интерфейс терминалов
                elif self._state.is_terminal_ui_open and not self._state.terminal_system.post_teleport_flag:
                    self._state.terminal_system.render()

                # стандартный рендерер
                elif not self._state.is_terminal_ui_open:
                    self._renderer.render()


                if self._input.spawn:
                    cords = self._input.spawn_pos + self._state.room_manager.active_room.offset

                    self._state.enemy_system.enemies.append(self._spawner._spawn_bookworm_mommy(*cords, 1.05 ** self._state.level_number, self._state))
                    # self._state.enemy_system.enemies.append(self._spawner._spawn_bookworm(*cords, 1.05 ** self._state.level_number, self._state))

                    self._input.spawn = False

                    # drop_item = random.choice(self._state.drop_pool)
                    # sprite_name = drop_item[1]
                    # self._state.collectable_system.items.append(drop_item[0](
                    #     x=cords.x,
                    #     y=cords.y,
                    #     size=35,
                    #     lifetime=15,
                    #     max_speed=600,
                    #     vx=900,
                    #     vy=0,
                    #     acceleration=-1000,
                    #     magnet=False,
                    #     collect_range=300,
                    #     sprite=self._state.assets[sprite_name],
                    #
                    # ))

            # ГЛАВНОЕ МЕНЮ
            else:
                self._state.menu_manager.active_screen.update(dt, pygame.mouse.get_pos(), events)
                self._state.menu_manager.active_screen.render(self._screen)
                if self._state.is_transition:
                    self._screen.blit(self._renderer.fx_surface, (0, 0))

                pygame.display.flip()
        pygame.quit()

    def _goto_new_level(self):
        # перезагружаем спрайты
        self._load_sprites(self._assets_manager)
        self._state.room_manager.switch_room_sprites(self._state.assets['wall_sprite'],
                                               self._state.assets['floor_sprite'],
                                                     self._state.assets['exit_sprite'])

        # чистим все системы
        self._state.decals_system.decals.clear()
        self._state.particle_system.particles.clear()
        self._state.enemy_system.enemies.clear()
        self._state.terminal_system.terminals.clear()

        # перерегенерируем уровень
        self._state.room_manager.initialize_level()

        # пересчитываем границы мира
        world_bounds = self._state.room_manager.world_bounds
        self._renderer._world_bounds = world_bounds
        self._renderer.world_surface = pygame.Surface((world_bounds.width, world_bounds.height))

        # переносим игрока на новый спавн
        spawn_center = self._state.room_manager.start_room.bounds.center
        self._state.player.body.rect.x, self._state.player.body.rect.y = spawn_center
        self._state.room_manager.update_active_room(self._state.player)

        # переносим камеру
        self._state.camera.position = pygame.Vector2(spawn_center) + Vector2(0, -20)
        self._state.camera.curr_center = self._state.camera.position.copy() + Vector2(0, -20)
        self._state.camera.prev_center = self._state.camera.position.copy() + Vector2(0, -20)

        # обновляем кэш миникарты
        self._map_renderer.initialize_room_data(self._state.room_manager, self._state)
        self._map_renderer.invalidate_cache()

        # обновляем данные terminal system
        self._state.terminal_system.room_manager = self._state.room_manager
        self._state.terminal_system.set_world_bounds(world_bounds)
        self._state.terminal_system.terminals = self._state.room_manager.terminals
        self._state.terminal_system.state = self._state
        self._state.terminal_system._walls_color = \
            config.MINIMAP_WALL_COLOR_LIST[self._state.level_seed - 1]

        # добавляем +1 к номеру уровня (этажа)
        self._state.level_number += 1
        self._state.stattracker.levels_completed += 1

        # увеличиваем тикающий урон по игроку
        if self._state.player.tick_damage <= config.PLAYER_TICK_DAMAGE_LIMIT:
            self._state.player.tick_damage += 1.5
        else:
            self._state.player.tick_damage = config.PLAYER_TICK_DAMAGE_LIMIT

    def _load_sprites(self, assets_manager: AssetManager) -> None:
        # Уровень
        self._state.level_seed = randint(1, 9)
        self._state.assets['wall_sprite'] = assets_manager.load_sprite(f"room/wall{self._state.level_seed}.png",
                                                 (config.TILE_SIZE, config.TILE_SIZE * 2))
        self._state.assets['floor_sprite'] = assets_manager.load_sprite(f"room/floor{self._state.level_seed}.png",
                                                  (config.TILE_SIZE, config.TILE_SIZE))
        self._state.assets['exit_sprite'] = assets_manager.load_sprite(f"room/exit{self._state.level_seed}.png",
                                                  (config.EXIT_SIZE, config.EXIT_SIZE))
        self._state.assets['exit_arrow'] = assets_manager.load_sprite(f"hud/exit_arrow.png", (48, 48))

        self._state.assets['chest_opened'] = assets_manager.load_sprite(f"room/chest_opened.png",
                                                                        (113, 85))
        self._state.assets['chest_closed'] = assets_manager.load_sprite(f"room/chest_closed.png",
                                                                        (113, 75))

        self._state.assets['slasher'] = assets_manager.load_sprite("characters/slasher.png",
                                                                         (config.PLAYER_SIZE,
                                                                          config.PLAYER_SIZE + 20))
        self._state.assets['electron'] = assets_manager.load_sprite("characters/electron.png",
                                                                   (config.PLAYER_SIZE,
                                                                    config.PLAYER_SIZE + 20))
        self._state.assets['tank'] = assets_manager.load_sprite("characters/tank.png",
                                                                   (config.PLAYER_SIZE,
                                                                    config.PLAYER_SIZE + 20))

        self._state.assets['pointer'] = assets_manager.load_sprite("weapons/pointer.png",
                                                                          (90, 60))
        self._state.assets['pointer_reload'] = assets_manager.load_sprite("weapons/pointer_reload.png",
                                                                          (90, 60))
        self._state.assets['pointer_crosshair'] = assets_manager.load_sprite("hud/pointer_crosshair.png",
                                                                             (20, 20))

        self._state.assets['tazer'] = assets_manager.load_sprite("weapons/tazer.png",
                                                                   (90, 60))
        self._state.assets['tazer_reload'] = assets_manager.load_sprite("weapons/tazer_reload.png",
                                                                          (90, 60))
        self._state.assets['tazer_crosshair'] = assets_manager.load_sprite("hud/tazer_crosshair.png",
                                                                             (20, 20))


        self._state.assets['bullet_indicator'] = assets_manager.load_sprite("hud/bullet_indicator.png",
                                                                            (40, 40))

        self._state.assets['hit_decal'] = assets_manager.load_sprite("decals/splash.png",
                                                                     (75, 75))
        self._state.assets['player_step'] = assets_manager.load_sprite("decals/step.png",
                                                                              (10, 10))
        self._state.assets['bookworm_step_sprite'] = assets_manager.load_sprite("decals/bookworm_step.png",
                                                                              (10, 10))
        self._state.assets['bookworm_sprite'] = assets_manager.load_sprite("enemies/bookworm.png",
                                                                           (40, 30))

        self._state.assets['hp_bar_back'] = assets_manager.load_sprite("hud/hp_bar_back.png",
                                                                       (140, 50))
        self._state.assets['hp_bar_top'] = assets_manager.load_sprite("hud/hp_bar_top.png",
                                                                       (140, 50))
        self._state.assets['hp_bar_fill'] = assets_manager.load_sprite("hud/hp_bar_fill.png",
                                                                       (1, 50))

        self._state.assets['terminal_sprite_active'] = assets_manager.load_sprite("room/terminal_active.png",
                                                                                 (config.TILE_SIZE,
                                                                                 int(config.TILE_SIZE * 1.33)))
        self._state.assets['terminal_sprite_inactive'] = assets_manager.load_sprite("room/terminal_inactive.png",
                                                                                  (config.TILE_SIZE,
                                                                                   int(config.TILE_SIZE * 1.33)))

        self._state.assets['scrap_sprites'] = [assets_manager.load_sprite(f"items/scrap_{i}.png",
                                                                          (28, 28)) for i in range(1, 6)]
        self._state.assets['scrap_ico'] = assets_manager.load_sprite("hud/scrap_ico.png", (32, 32))

        self._state.assets['dash_ico'] = assets_manager.load_sprite("hud/dash_ico.png", (48, 32))
        self._state.assets['slash_ico'] = assets_manager.load_sprite("hud/slash_ico.png", (48, 32))

        # Бонусы
        self._state.assets['cassette'] = assets_manager.load_sprite("items/cassette.png", (35, 30))
        self._state.assets['floppy'] = assets_manager.load_sprite("items/floppy.png", (35, 35))
        self._state.assets['monster'] = assets_manager.load_sprite("items/monster.png", (21, 45))
        self._state.assets['monsterwhite'] = assets_manager.load_sprite("items/monsterwhite.png", (21, 45))
        self._state.assets['clock'] = assets_manager.load_sprite("items/clock.png", (35, 22))
        self._state.assets['nothing'] = assets_manager.load_sprite("items/nothing.png", (35, 35))

        self._state.assets['main_menu_art'] = assets_manager.load_sprite("menu/main_menu_art.png")

        self._state.assets['n'] = assets_manager.load_sprite("menu/N.png")
        self._state.assets['o'] = assets_manager.load_sprite("menu/O.png")
        self._state.assets['g'] = assets_manager.load_sprite("menu/G.png")
        self._state.assets['u'] = assets_manager.load_sprite("menu/U.png")
        self._state.assets['m'] = assets_manager.load_sprite("menu/M.png")
        self._state.assets['!'] = assets_manager.load_sprite("menu/!.png")

    def _constrain_window(self, req_w: int, req_h: int, width_changed: bool) -> None:
        # минимальный размер
        w = max(req_w, self.min_window_width)
        h = max(req_h, self.min_window_height)

        if width_changed:
            h = w / self.target_aspect
        else:
            w = h * self.target_aspect

        w, h = int(w), int(h)

        # пересоздаём поверхность с новыми размерами
        flags = pygame.FULLSCREEN if self.is_fullscreen else pygame.RESIZABLE
        self._screen = pygame.display.set_mode((w, h), flags)

        # в меню
        for menu_screen in self._state.menu_screens.values():
            menu_screen.resize(*self._screen.get_size())
        self._fx_layer = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        # обновляем ссылки
        if self._renderer:
            self._renderer._screen = self._screen
            self._renderer.fx_surface = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
            self._ui_renderer._screen = self._screen
            self._state.terminal_system._screen = self._screen
            self._map_renderer._screen = self._screen

    # переключает между оконным и полноэкранным режимом
    def _toggle_fullscreen(self) -> None:
        pass
        # self.is_fullscreen = not self.is_fullscreen
        # flags = pygame.FULLSCREEN if self.is_fullscreen else pygame.RESIZABLE
        # size = (0, 0) if self.is_fullscreen else self._screen.get_size()
        # self._screen = pygame.display.set_mode(size, flags)
        #
        # # в меню
        # self._state.menu_manager.active_screen.resize(*self._screen.get_size())
        # self._fx_layer = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        # # обновляем ссылки
        # self._renderer._screen = self._screen
        # self._renderer.fx_surface = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        # self._ui_renderer._screen = self._screen
        # self._state.terminal_system._screen = self._screen
        # self._map_renderer._screen = self._screen

    def _start_game(self) -> None:
        # инициализируем игру
        self._state.is_transition = True

        # перезагружаем спрайты
        self._load_sprites(self._assets_manager)

        # инициализируем уровень ДО игрока чтобы взять координаты спавна
        self._state.room_manager = RoomManager(wall_sprite=self._state.assets['wall_sprite'],
                                               floor_sprite=self._state.assets['floor_sprite'],
                                               exit_sprite=self._state.assets['exit_sprite'],
                                               state=self._state)
        spawn_center = self._state.room_manager.active_room.bounds.center

        # инструменты и системы
        self._input = InputHandler(self._state)
        self._state.collision_system = CollisionSystem(self._state)
        self._weapon_system = WeaponSystem(self._state)

        self._state.projectile_system = ProjectileSystem(self._state)
        self._state.particle_system = ParticleSystem()
        self._state.collectable_system = CollectableSystem(self._state)
        self._state.enemy_system = EnemySystem()
        self._state.decals_system = DecalSystem()
        self._state.terminal_system = TerminalSystem(self._screen, self._state)
        self._spawner = Spawner(self._state)

        self._state.stattracker = StatTracker()

        self._state.camera = Camera()
        self._state.camera.position = pygame.Vector2(spawn_center)
        self._state.camera.curr_center = self._state.camera.position.copy()
        self._state.camera.prev_center = self._state.camera.position.copy()

        # определяем точку спавна
        spawn_center = self._state.room_manager.start_room.bounds.center

        self._state.player = self._state.character_pool[self._state.character](
            x=spawn_center[0] - config.PLAYER_SIZE / 2,
            y=spawn_center[1] - config.PLAYER_SIZE / 2,
            state=self._state
        )

        # kамера тоже стартует с центра стартовой комнаты
        self._state.camera.position = pygame.Vector2(spawn_center) + Vector2(0, -20)
        self._state.camera.curr_center = self._state.camera.position.copy() + Vector2(0, -20)
        self._state.camera.prev_center = self._state.camera.position.copy() + Vector2(0, -20)

        # инициализируем стартовое оружие и скиллы
        self._state.weapon = self._state.weapon_pool[self._state.player.character_config['weapon']](self._state)
        self._state.player.weapon = self._state.weapon

        self._state.player.first_skill =\
            self._state.skills_pool[self._state.player.character_config['first_skill']](self._state)
        self._state.player.second_skill =\
            self._state.skills_pool[self._state.player.character_config['second_skill']](self._state)

        self._state.room_manager.update_active_room(self._state.player)

        # рендереры
        self._map_renderer = MinimapRenderer(self._screen, self._state)
        self._ui_renderer = UIRenderer(self._screen, self._state)
        self._ui_renderer._map_renderer = self._map_renderer
        self._renderer = Renderer(self._state, self._screen, self._state.room_manager.world_bounds, self._ui_renderer)

        # resizable объекты (требуют изменений при изменении размеров окна)
        self._state.resizable_elements.append(self._ui_renderer)
        self._state.resizable_elements.append(self._state.terminal_system)
        self._state.resizable_elements.append(self._map_renderer)

        # пул предметов для дропа
        self._state.drop_pool = [
            (Cassette, 'cassette'),
            (Floppy, 'floppy'),
            (Monster, 'monster'),
            (MonsterWhite, 'monsterwhite'),
            (Clock, 'clock')
        ]
        self._state.items_in_game = self._state.drop_pool.copy()

        # заполняем инвентарь пустышками
        self._state.stattracker.inventory = dict()
        for item_name in [item[1] for item in self._state.drop_pool]:
            self._state.player.inventory[item_name.capitalize()] = [0, self._state.assets[item_name]]
            self._state.stattracker.inventory[item_name.capitalize()] = 0
