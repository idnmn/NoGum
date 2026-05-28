import random
import pygame
from pygame import Vector2
from services.particle_system import Particle
from models.collidable import CollisionBody
from models.game_state import GameState
from models.player import Player


# общий класс для дропнутых предметов
class Collectable():
    def __init__(self, x: float, y: float, size: int, lifetime: float,
                 max_speed:float, collect_range: float) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"collectable"}
        )

        self.lifetime = lifetime
        self.is_active = True
        self._max_speed = max_speed
        self._collect_range = collect_range

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def update(self, dt: float, player: Player) -> None:
        # двигаемся быстрее, по мере приближения к игроку
        dist_to_player = Vector2(self.rect.center).distance_to(player.rect.center)
        dir_to_player = (pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)).normalize()
        current_speed = self._max_speed * (1 - (dist_to_player / self._collect_range) ** 2)

        # ограничиваем максимальную скорость
        if current_speed > self._max_speed:
            scale = self._max_speed / current_speed
            current_speed *= scale

        direction = dir_to_player * current_speed

        self.body.vx = direction.x
        self.body.vy = direction.y

        # защита от дрейфа
        if current_speed < 1.0:
            self.body.vx = 0.0
            self.body.vy = 0.0

        self.body.rect.x += self.body.vx * dt
        self.body.rect.y += self.body.vy * dt

        self.lifetime -= dt

    def collect(self, state: GameState) -> None:
        pass

    def spawn_particles(self, state: GameState) -> None:
        pass


# местные хилки
class EnergyCell(Collectable):
    def __init__(self, x: float, y: float, size: int, lifetime: float,
                 max_speed: float, collect_range: float) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range)
        self._scale = random.randint(3, 8)

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (255, 215, 80), self.rect.center,
                           int((self.rect.width//2) * (self._scale / 4)), 0)

    def collect(self, state: GameState) -> None:
        state.player.hp += self._scale
        if state.player.hp > state.player.max_hp:
            state.player.hp = state.player.max_hp

    def spawn_particles(self, state: GameState) -> None:
        pos = self.body.rect.center

        for _ in range(self._scale):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(300, 500)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=(255, 215, 80),
                size=random.uniform(2, 4)
            ))