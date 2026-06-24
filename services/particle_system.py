import pygame
import random

from pygame import Vector2

from configs import config, skills_stats
import math
from dataclasses import dataclass

from models.game_state import GameState



class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, lifetime: float, max_lifetime: float,
                 color: tuple[int, int, int], size: float, is_square: bool = False) -> None:
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.lifetime = lifetime
        self.max_lifetime = max_lifetime
        self.color = color
        self.is_square = is_square
        self.size = size

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def render(self, surface: pygame.Surface) -> None:
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (self.color[0], self.color[1], self.color[2], alpha)

        draw_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

        if not self.is_square:
            pygame.draw.circle(draw_surface, color, (self.size, self.size), int(self.size))
        else:
            pygame.draw.rect(draw_surface, color, (0, 0, self.size * 2, self.size * 2))

        surface.blit(draw_surface, self.rect)

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.95
        self.vy *= 0.95
        self.lifetime -= dt

class SinParticle(Particle):
    def __init__(self, x: float, y: float, vx: float, vy: float, lifetime: float, max_lifetime: float,
                 color: tuple[int, int, int], size: float, is_square: bool = False,
                 sin_amp: float = 0.0, sin_freq: float = 20.0) -> None:
        super().__init__(x, y, vx, vy, lifetime, max_lifetime, color, size, is_square)
        self.sin_amp = sin_amp
        self.sin_freq = sin_freq
        self.time_par = 0.0

    def update(self, dt: float) -> None:
        self.time_par += dt * self.sin_freq
        self.time_par %= 360
        print(self.time_par)

        vel = Vector2(self.vx, self.vy)
        if vel.magnitude() > 0:
            dir = vel.normalize()
        else:
            dir = Vector2(0, 0)
        offset_vector = (dir.rotate(90) * (math.cos(self.time_par) * self.sin_amp))

        self.x += self.vx * dt + offset_vector.x
        self.y += self.vy * dt + offset_vector.y
        self.lifetime -= dt


class ParticleSystem:
    def __init__(self, state: GameState) -> None:
        self._state = state
        self.particles: list[Particle] = []

        self._limit = 5000

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
        for _ in range(random.randint(3, 5)):
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
                size=random.uniform(2, 4),
                is_square=True
            ))

    def spawn_dash_reloaded(self, pos: tuple[float, float], color: tuple[int, int, int] = skills_stats.UI_DASH_COLOR) -> None:
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
                color=color,
                size=3
            ))

    def spawn_dashed(self, pos: tuple[float, float], color: tuple[int, int, int] = skills_stats.UI_DASH_COLOR) -> None:
        for _ in range(36):
            angle = math.radians(10 * _)
            speed = 500
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            self.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.2,
                max_lifetime=0.2,
                color=color,
                size=4
            ))

    def spawn_while_dash(self, pos: tuple[float, float], dir: pygame.Vector2,
                         color: tuple[int, int, int] = skills_stats.UI_DASH_COLOR, owner_size: int = 10) -> None:
        for _ in range(random.randint(2, 3)):
            speed = random.uniform(600, 800)
            vx, vy = -dir * speed
            rand_x, rand_y = (random.randint(int(-owner_size * 0.8), int(owner_size * 0.8)),
                              random.randint(int(-owner_size * 0.8), int(owner_size * 0.8)))

            self.particles.append(Particle(
                x=pos[0] + rand_x, y=pos[1] + rand_y,
                vx=vx, vy=vy,
                lifetime=0.2,
                max_lifetime=0.2,
                color=color,
                size=random.uniform(2, 4)
            ))

    def spawn_slash_marked(self, pos: tuple[float, float], owner_size: int) -> None:
        for _ in range(random.randint(0, 1)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            pos_x, pos_y = pygame.Vector2(pos[0], pos[1]) + Vector2(owner_size / 2).rotate_rad(angle)

            self.particles.append(Particle(
                x=pos_x, y=pos_y,
                vx=0, vy=0,
                lifetime=0.4,
                max_lifetime=0.4,
                color=skills_stats.UI_DASH_COLOR,
                size=random.uniform(2, 4)
            ))

    def spawn_electricity_marked(self, pos: tuple[float, float], owner_size: int) -> None:
        angle = random.uniform(0, 6.2832)  # 2 * pi
        pos_x, pos_y = pygame.Vector2(pos[0], pos[1]) + Vector2(owner_size / 4).rotate_rad(angle)
        vel = Vector2(1, 0).rotate_rad(angle) * random.uniform(100, 200)

        self.particles.append(Particle(
            x=pos_x, y=pos_y,
            vx=vel.x, vy=vel.y,
            lifetime=0.4,
            max_lifetime=0.4,
            color=config.ELECTRICITY_COLOR,
            size=random.uniform(1, 3),
            is_square=True
        ))

    def spawn_slash(self, origin: tuple[float, float], end_pos: tuple[float, float], radius: int, facing_right,
                    color: tuple[int, int, int] = skills_stats.UI_DASH_COLOR) -> None:
        count = random.randint(int(radius * 0.5), int(radius * 0.7))
        if facing_right:
            dir = (end_pos - origin).normalize().rotate(90)
        else:
            dir = (end_pos - origin).normalize().rotate(-90)

        for _ in range(count):
            angle = math.degrees(math.atan2(end_pos[1] - origin[1], end_pos[0] - origin[0]))
            dist = random.uniform(0, radius * 0.6)
            pos = origin + Vector2(dist).rotate(angle - 30)
            rand_pos = random.randint(-int(radius * 0.15), int(radius * 0.15))
            size_range = 6 * dist / radius
            speed = 900

            self.particles.append(Particle(
                x=pos.x + rand_pos, y=pos.y + rand_pos,
                vx=dir.x * speed, vy=dir.y * speed,
                lifetime=0.15,
                max_lifetime=0.15,
                color=color,
                size=1 + size_range,
            ))

    def spawn_open_chest(self, pos: tuple[float, float]) -> None:
        for _ in range(108):
            angle = math.radians(7.5 * _)
            speed = random.uniform(300, 1000)
            lifetime = random.uniform(0.3, 0.8)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            self.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=lifetime,
                max_lifetime=lifetime,
                color=(175, 60, 60),
                size=5
            ))

    def spawn_tazer_projectile(self, pos: tuple[float, float]) -> None:
        for _ in range(random.randint(2, 3)):
            rand_x = random.uniform(-5, 5)
            rand_y = random.uniform(-5, 5)

            self.particles.append(Particle(
                x=pos[0] + rand_x, y=pos[1] + rand_y,
                vx=0, vy=0,
                lifetime=0.1,
                max_lifetime=0.1,
                color=self._state.weapon.signature_color,
                size=random.uniform(1, 3),
                is_square=True
            ))

    def spawn_magnet_dash_trail(self, pos: tuple[float, float],
                                color: tuple[int, int, int] = skills_stats.UI_MAGNET_COLOR, owner_size: int = 10) -> None:
        for _ in range(random.randint(8, 10)):
            rand_x, rand_y = (random.randint(int(-owner_size * 0.8), int(owner_size * 0.8)),
                              random.randint(int(-owner_size * 0.8), int(owner_size * 0.8)))

            self.particles.append(Particle(
                x=pos[0] + rand_x, y=pos[1] + rand_y,
                vx=0, vy=0,
                lifetime=0.2,
                max_lifetime=0.2,
                color=color,
                size=random.uniform(1, 4),
                is_square=True
            ))

    def spawn_magnet_dashed(self, pos: tuple[float, float], color: tuple[int, int, int] = skills_stats.UI_MAGNET_COLOR) -> None:
        for _ in range(36):
            angle = math.radians(10 * _)
            speed = 300
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            self.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.7,
                max_lifetime=0.7,
                color=color,
                size=4,
                is_square=True,
            ))

    def spawn_zap_projectile_trail(self, pos: tuple[float, float], dir: Vector2) -> None:
        for _ in range(random.randint(5, 8)):
            rand_x = random.uniform(-5, 5)
            rand_y = random.uniform(-5, 5)
            vel = dir.rotate(random.uniform(135, 225)) * random.uniform(100, 200)

            self.particles.append(Particle(
                x=pos[0] + rand_x, y=pos[1] + rand_y,
                vx=vel.x, vy=vel.y,
                lifetime=1.0,
                max_lifetime=1.0,
                color=self._state.weapon.signature_color,
                size=random.uniform(2, 4),
                is_square=True
            ))

    def spawn_zap_projectile(self, pos: tuple[float, float], size) -> None:
        for _ in range(36):
            angle = math.radians(10 * _)
            speed = random.uniform(100, 200)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            self.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._state.player.signature_color,
                size=random.uniform(2, 4),
            ))

    def spawn_magnet_hitted(self, pos: tuple[float, float], color: tuple[int, int, int] = skills_stats.UI_MAGNET_COLOR) -> None:
        for _ in range(36):
            angle = math.radians(10 * _)
            speed = 400
            vx, vy = -pygame.Vector2(speed, 0).rotate_rad(angle)
            x, y = pygame.Vector2(pos[0], pos[1]) + pygame.Vector2(speed, 0).rotate_rad(angle) * 0.3

            self.particles.append(Particle(
                x=x, y=y,
                vx=vx, vy=vy,
                lifetime=0.5,
                max_lifetime=0.5,
                color=color,
                size=3,
                is_square=True
            ))


    def update(self, dt: float) -> None:
        for p in self.particles:
            p.update(dt)

        self.particles = [p for p in self.particles if p.lifetime > 0]

        while len(self.particles) > self._limit:
            self.particles.pop(0)

