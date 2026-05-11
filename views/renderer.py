import pygame
import config
from services.enemy_system import EnemySystem
from services.particle_system import ParticleSystem
from services.projectile_system import ProjectileSystem
from models.game_state import GameState
from models.room_manager import RoomManager
from models.camera import Camera
from views.ui_renderer import UIRenderer


# рендерер
class Renderer:
    def __init__(self, screen: pygame.Surface, world_bounds: pygame.Rect, ui_renderer: UIRenderer) -> None:
        self._screen = screen
        self._world_bounds = world_bounds
        self._ui_renderer = ui_renderer
        self.debug_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # поверхность, на которой рисуется весь мир в абсолютных координатах
        self.world_surface = pygame.Surface((world_bounds.width, world_bounds.height), pygame.SRCALPHA)

        # поверхность для отрисовки теней
        self.shadow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        # буфер для финального кадра перед масштабированием
        self._viewport_buffer = pygame.Surface((config.INTERNAL_WIDTH, config.INTERNAL_HEIGHT))

    def render(self, state: GameState, room_manager: RoomManager, camera: Camera) -> None:
        # очищаем экран
        self.world_surface.fill(config.BACKGROUND_COLOR)
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
        for decal in state.decals_system.decals:
            decals_queue.append(decal)
        decals_queue.sort(key=lambda obj: obj.rect.bottom) # сортируем

        for decal in decals_queue:
            decal.render(self.world_surface)

        # рендерим тени
        for shadow in state.decals_system.shadows:
            shadow.render(self.shadow_surface, room_manager.active_room.offset)
        self.world_surface.blit(self.shadow_surface, room_manager.active_room.offset)

        # добавляем стены в очередь
        for room in rooms_to_draw:
            render_queue.extend(room.walls)

        # добавляем игрока в очередь
        if state.player:
            render_queue.append(state.player)

        # добавляем снаряды в очередь
        render_queue += state.projectile_system.projectiles

        # добавляем частицы в очередь
        render_queue += state.particle_system.particles

        # добавляем врагов в очередь
        render_queue += state.enemy_system.enemies

        # сортируем очередь по y координате
        render_queue.sort(key=lambda obj: obj.rect.bottom)

        # рендерим все объекты из очереди
        for obj in render_queue:
            obj.render(self.world_surface)

        # рендерим inworld часть ui
        self._ui_renderer.render_in_world(state, self.world_surface)

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
        self._ui_renderer.render_out_world(state)

        # сменяем кадр
        pygame.display.flip()

