import pygame
import random
import config
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
    def __init__(self, max_particles: int = 200) -> None:
        self.particles: list[Particle] = []

        # for _ in range(max_particles):
        #     self._pool.append(Particle(0,0,0,0,0,0,(0,0,0),0))

    def spawn_impact(self, pos: tuple[float, float], color: tuple[int, int, int] = (255, 200, 50)) -> None:
        for _ in range(config.IMPACT_PARTICLE_COUNT):
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

    def update(self, dt: float) -> None:
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vx *= 0.95
            p.vy *= 0.95
            p.lifetime -= dt

        self.particles = [p for p in self.particles if p.lifetime > 0]
