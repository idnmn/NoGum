import pygame
import random
import config
import math
from dataclasses import dataclass

@dataclass
class Particle:
    x: float; y: float; vx: float; vy: float
    lifetime: float; max_lifetime: float; color: tuple[int, int, int]; size: float

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def render(self, surface: pygame.Surface) -> None:
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size), )

class ParticleSystem:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

        self._limit = 500

    def spawn_wall_impact(self, pos: tuple[float, float], color: tuple[int, int, int] = (255, 200, 50)) -> None:
        for _ in range(config.WALL_IMPACT_PARTICLE_COUNT):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(config.IMPACT_PARTICLE_SPEED * 0.5, config.IMPACT_PARTICLE_SPEED)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            self.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=config.IMPACT_PARTICLE_LIFETIME,
                max_lifetime=config.IMPACT_PARTICLE_LIFETIME,
                color=color,
                size=random.uniform(2, 4)
            ))

    def spawn_enemy_impact(self, pos: tuple[float, float], color: tuple[int, int, int] = (255, 200, 50)) -> None:
        for _ in range(config.ENEMY_IMPACT_PARTICLE_COUNT):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(config.IMPACT_PARTICLE_SPEED * 0.5, config.IMPACT_PARTICLE_SPEED)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            self.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=config.IMPACT_PARTICLE_LIFETIME,
                max_lifetime=config.IMPACT_PARTICLE_LIFETIME,
                color=color,
                size=random.uniform(2, 4)
            ))

    def spawn_player_damaged(self, pos: tuple[float, float], color: tuple[int, int, int] = (250, 255, 60)) -> None:
        for _ in range(random.randint(4, 7)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(100, 150)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)
            rand_x, rand_y = random.randint(-config.PLAYER_SIZE, config.PLAYER_SIZE), random.randint(-config.PLAYER_SIZE, config.PLAYER_SIZE)

            self.particles.append(Particle(
                x=pos[0] + rand_x, y=pos[1] + rand_y,
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=color,
                size=random.uniform(2, 4)
            ))

    def spawn_dash_reloaded(self, pos: tuple[float, float]) -> None:
        for _ in range(36):
            angle = math.radians(10 * _)
            speed = 700
            vx, vy = -pygame.Vector2(speed, 0).rotate_rad(angle)
            x, y = pygame.Vector2(pos[0], pos[1]) + pygame.Vector2(speed, 0).rotate_rad(angle) * 0.12

            self.particles.append(Particle(
                x=x, y=y,
                vx=vx, vy=vy,
                lifetime=0.2,
                max_lifetime=0.2,
                color=config.UI_DASH_COLOR,
                size=3
            ))

    def spawn_dashed(self, pos: tuple[float, float]) -> None:
        for _ in range(36):
            angle = math.radians(10 * _)
            speed = 500
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            self.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.2,
                max_lifetime=0.2,
                color=config.UI_DASH_COLOR,
                size=4
            ))

    def spawn_while_dash(self, pos: tuple[float, float], dir: pygame.Vector2) -> None:
        for _ in range(random.randint(2, 3)):
            speed = random.uniform(600, 800)
            vx, vy = dir * speed
            rand_x, rand_y = (random.randint(int(-config.PLAYER_SIZE * 0.8), int(config.PLAYER_SIZE * 0.8)),
                              random.randint(int(-config.PLAYER_SIZE * 0.8), int(config.PLAYER_SIZE * 0.8)))

            self.particles.append(Particle(
                x=pos[0] + rand_x, y=pos[1] + rand_y,
                vx=vx, vy=vy,
                lifetime=0.2,
                max_lifetime=0.2,
                color=config.UI_DASH_COLOR,
                size=random.uniform(2, 4)
            ))

    def update(self, dt: float) -> None:
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vx *= 0.95
            p.vy *= 0.95
            p.lifetime -= dt

        self.particles = [p for p in self.particles if p.lifetime > 0]

        while len(self.particles) > self._limit:
            self.particles.pop(0)
