import pygame
from configs import config
from models.game_state import GameState
from views.ui_renderer import UIRenderer


# рендерер
class Renderer:
    def __init__(self, state: GameState, screen: pygame.Surface,
                 world_bounds: pygame.Rect, ui_renderer: UIRenderer) -> None:
        self._state = state
        self._screen = screen
        self._world_bounds = world_bounds
        self._ui_renderer = ui_renderer
        self.debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        self.fx_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # поверхность, на которой рисуется весь мир в абсолютных координатах
        self.world_surface = pygame.Surface((world_bounds.width, world_bounds.height), pygame.SRCALPHA)

        # поверхность для отрисовки теней
        self.shadow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA).convert_alpha()

        # буфер для финального кадра перед масштабированием
        self._viewport_buffer = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))

    def render(self, flip_flag: bool = True) -> None:
        camera = self._state.camera
        room_manager = self._state.room_manager

        # очищаем экран
        self.world_surface.fill((*config.BACKGROUND_COLOR, 255))
        self.shadow_surface.fill((0, 0, 0, 0))

        # очередь рендера
        render_queue = []
        decals_queue = []

        # во время перехода камеры рисуем обе комнаты
        rooms_to_draw = []
        if camera.is_transitioning and room_manager.prev_active_room:
            rooms_to_draw.append(room_manager.prev_active_room)
        if room_manager.active_room:
            rooms_to_draw.append(room_manager.active_room)

        # отрисовываем полы вне очереди
        for room in rooms_to_draw:
            self.world_surface.blit(room.floor_surface, (room.offset.x, room.offset.y - config.TILE_SIZE))

        # рендерим декали
        for decal in self._state.decals_system.decals:
            decals_queue.append(decal)
        decals_queue.sort(key=lambda obj: obj.rect.bottom) # сортируем

        for decal in decals_queue:
            decal.render(self.world_surface)

        # рендерим тени
        for shadow in self._state.decals_system.shadows:
            shadow.render(self.shadow_surface, room_manager.active_room.offset)
        self.world_surface.blit(self.shadow_surface, room_manager.active_room.offset)

        # добавляем стены и интерактивные объедки в очередь
        for room in rooms_to_draw:
            render_queue.extend(room.walls)
            if room.terminal:
                render_queue.append(room.terminal)
            if room.chest:
                render_queue.append(room.chest)
            if room.exit:
                room.exit.render(self.world_surface)

        # добавляем игрока в очередь
        if self._state.player:
            render_queue.append(self._state.player)

        # добавляем снаряды в очередь
        render_queue += self._state.projectile_system.projectiles

        # добавляем частицы в очередь
        render_queue += self._state.particle_system.particles

        # добавляем врагов в очередь
        render_queue += self._state.enemy_system.enemies

        # добавляем подбираемые предметы в очередь
        render_queue += self._state.collectable_system.items

        # сортируем очередь по y координате
        render_queue.sort(key=lambda obj: obj.rect.bottom)

        # рендерим все объекты из очереди
        for obj in render_queue:
            obj.render(self.world_surface)

        # рендерим inworld часть ui
        self._ui_renderer.render_in_world(self.world_surface)

        if room.exit:
            if room.exit.is_near_player:
                self.world_surface.blit(room.exit.arrow_sprite, (room.exit.body.rect.x + room.exit.body.rect.width / 2 - 24,
                                                 room.exit.body.rect.y - 30))

        # вычисляем координаты вьюпорта
        view_x = int(camera.position.x + camera.shake_offset.x - config.INTERNAL_WIDTH / 2)
        view_y = int(camera.position.y + camera.shake_offset.y - config.INTERNAL_HEIGHT / 2)
        view_rect = pygame.Rect(view_x, view_y, config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT)

        view_rect.clamp_ip(self._world_bounds) # ограничиваем размерами мира

        visible_chunk = self.world_surface.subsurface(view_rect) # вырезаем видимый чанк

        # масштабируем под размер экрана
        scaled_view = pygame.transform.scale(visible_chunk, self._screen.get_size())

        # выводим на экран
        self._screen.blit(scaled_view, (0, 0))

        # дебаг отрисовка
        if config.DRAW_PATH:
            self._screen.blit(self.debug_surface, (0, 0))

        # рендерим outworld часть ui
        self._ui_renderer.render_out_world()

        # рендерим fx слой
        self._screen.blit(self.fx_surface, (0, 0))

        # сменяем кадр
        if flip_flag:
            pygame.display.flip()

