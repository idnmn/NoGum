import random
import pygame
from pygame import Vector2

import config
from services.particle_system import Particle
from models.collidable import CollisionBody
from models.game_state import GameState
from models.player import Player


# общий класс для дропнутых предметов
class Collectable():
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 acceleration: float = 0.0, magnet: bool = True, vx: float = 0.0, vy: float = 0.0) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"collectable"},
            vx=vx,
            vy=vy
        )

        self.lifetime = lifetime
        self.is_active = True
        self._max_speed = max_speed
        self._collect_range = collect_range
        self._acceleration = acceleration

        self.magnet = magnet

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def update(self, dt: float, player: Player) -> None:
        if self.magnet:
            # двигаемся быстрее, по мере приближения к игроку
            dist_to_player = Vector2(self.rect.center).distance_to(player.rect.center)
            dir_to_player = (pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)).normalize()
            current_speed = self._max_speed * (1 - (dist_to_player / self._collect_range) ** 2)
        else:
            current_speed = Vector2(self.body.vx, self.body.vy).magnitude()
            if current_speed > 0:
                dir_to_player = Vector2(self.body.vx, self.body.vy).normalize()
            else:
                dir_to_player = Vector2(0)

        # ограничиваем максимальную скорость
        if current_speed > self._max_speed:
            scale = self._max_speed / current_speed
            current_speed *= scale

        direction = dir_to_player * current_speed

        self.body.vx = direction.x
        self.body.vy = direction.y

        acceleration = self._acceleration * dir_to_player
        self.body.vx += acceleration.x * dt
        self.body.vy += acceleration.y * dt

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
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 acceleration: float = 0.0, magnet: bool = True, vx: float = 0.0, vy: float = 0.0) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range, acceleration, magnet, vx, vy)
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


# местная валюта
class Scrap(Collectable):
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 sprites: list[pygame.Surface], acceleration: float = 0.0, magnet: bool = True,
                 vx: float = 0.0, vy: float = 0.0) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range, acceleration, magnet, vx, vy)
        self._scale = random.randint(1, 3)

        g = random.randint(150, 200)
        self._color = (g, g, g)
        self._sprite = random.choice(sprites)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self._sprite, (self.rect.x, self.rect.y))

    def collect(self, state: GameState) -> None:
        state.player.scrap += self._scale
        state.stattracker.scrap_collected += self._scale

    def spawn_particles(self, state: GameState) -> None:
        pos = self.body.rect.center

        for _ in range(random.randint(5, 8)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(100, 300)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._color,
                size=random.uniform(3, 5)
            ))


# бонусы
class BonusItem(Collectable):
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 sprite: pygame.Surface, acceleration: float = 0.0, magnet: bool = True,
                 vx: float = 0.0, vy: float = 0.0) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range, acceleration, magnet, vx, vy)
        self.sprite = sprite
        self.name = ''

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.sprite, (self.rect.x, self.rect.y))

    def collect(self, state: GameState) -> None:
        state.player.inventory[self.name][0] += 1

    def spawn_particles(self, state: GameState) -> None:
        pos = self.body.rect.center

        for _ in range(random.randint(10, 13)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(300, 500)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._color,
                size=random.uniform(3, 5)
            ))

# +скорость
class Cassette(BonusItem):
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 sprite: pygame.Surface, acceleration: float = 0.0, magnet: bool = True,
                 vx: float = 0.0, vy: float = 0.0) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range, sprite, acceleration, magnet, vx, vy)

        self._color = (215, 175, 175)
        self.name = 'Cassette'

    def collect(self, state: GameState) -> None:
        super().collect(state)

        state.player.max_speed *= 1.05

        if state.player.max_speed >= config.PLAYER_MAX_SPEED_LIMIT:
            state.player.max_speed = config.PLAYER_MAX_SPEED_LIMIT

            if (Cassette, 'cassette') in state.drop_pool:
                state.drop_pool.remove((Cassette, 'cassette'))

# +урон
class Floppy(BonusItem):
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 sprite: pygame.Surface, acceleration: float = 0.0, magnet: bool = True,
                 vx: float = 0.0, vy: float = 0.0) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range, sprite, acceleration, magnet, vx, vy)

        self._color = (250, 220, 190)
        self.name = 'Floppy'

    def collect(self, state: GameState) -> None:
        super().collect(state)

        state.player.weapon.damage_coef += 0.05

        if state.player.weapon.damage_coef >= config.DAMAGE_COEF_LIMIT:
            state.player.weapon.damage_coef = config.DAMAGE_COEF_LIMIT

            if (Floppy, 'floppy') in state.drop_pool:
                state.drop_pool.remove((Floppy, 'floppy'))

# +макс хп
class Monster(BonusItem):
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 sprite: pygame.Surface, acceleration: float = 0.0, magnet: bool = True,
                 vx: float = 0.0, vy: float = 0.0) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range, sprite, acceleration, magnet, vx, vy)

        self._color_main = (65, 65, 65)
        self._color_secondary = (85, 225, 0)
        self.name = 'Monster'

    def collect(self, state: GameState) -> None:
        super().collect(state)

        state.player.max_hp += 10
        state.player.hp += 10

        if state.player.max_hp >= config.PLAYER_MAX_HP_LIMIT:
            state.player.max_hp = config.PLAYER_MAX_HP_LIMIT
            state.player.hp = state.player.max_hp

            if (Monster, 'monster') in state.drop_pool:
                state.drop_pool.remove((Monster, 'monster'))

    def spawn_particles(self, state: GameState) -> None:
        pos = self.body.rect.center

        for _ in range(random.randint(7, 10)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(300, 500)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._color_main,
                size=random.uniform(3, 5)
            ))

        for _ in range(random.randint(5, 7)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(400, 600)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._color_secondary,
                size=random.uniform(3, 5)
            ))

# -тикающий урон
class MonsterWhite(BonusItem):
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 sprite: pygame.Surface, acceleration: float = 0.0, magnet: bool = True,
                 vx: float = 0.0, vy: float = 0.0) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range, sprite, acceleration, magnet, vx, vy)

        self._color_main = (255, 255, 255)
        self._color_secondary = (120, 215, 250)
        self.name = 'Monsterwhite'

    def collect(self, state: GameState) -> None:
        super().collect(state)

        state.player.tick_damage_coef -= 0.05

        if state.player.tick_damage_coef <= config.PLAYER_TICK_DAMAGE_COEF_LIMIT:
            state.player.tick_damage_coef = config.PLAYER_TICK_DAMAGE_COEF_LIMIT

            if (MonsterWhite, 'monsterwhite') in state.drop_pool:
                state.drop_pool.remove((MonsterWhite, 'monsterwhite'))

    def spawn_particles(self, state: GameState) -> None:
        pos = self.body.rect.center

        for _ in range(random.randint(7, 10)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(300, 500)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._color_main,
                size=random.uniform(3, 5)
            ))

        for _ in range(random.randint(5, 7)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(400, 600)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._color_secondary,
                size=random.uniform(3, 5)
            ))

# -кд скиллов
class Clock(BonusItem):
    def __init__(self, x: float, y: float, size: int, lifetime: float, max_speed: float, collect_range: float,
                 sprite: pygame.Surface, acceleration: float = 0.0, magnet: bool = True,
                 vx: float = 0.0, vy: float = 0.0) -> None:
        super().__init__(x, y, size, lifetime, max_speed, collect_range, sprite, acceleration, magnet, vx, vy)

        self._color_main = (0, 20, 80)
        self._color_secondary = (240, 10, 80)
        self.name = 'Monster'

    def collect(self, state: GameState) -> None:
        super().collect(state)

        state.player.first_skill.cool_down_coef -= 0.05
        state.player.second_skill.cool_down_coef -= 0.05

        if state.player.first_skill.cool_down_coef < config.SKILLS_COOLDOWN_COEF_LIMIT:
            state.player.first_skill.cool_down_coef = config.SKILLS_COOLDOWN_COEF_LIMIT
            state.player.second_skill.cool_down_coef = config.SKILLS_COOLDOWN_COEF_LIMIT

            if (Clock, 'clock') in state.drop_pool:
                state.drop_pool.remove((Clock, 'clock'))

    def spawn_particles(self, state: GameState) -> None:
        pos = self.body.rect.center

        for _ in range(random.randint(7, 10)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(300, 500)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._color_main,
                size=random.uniform(3, 5)
            ))

        for _ in range(random.randint(5, 7)):
            angle = random.uniform(0, 6.2832)  # 2 * pi
            speed = random.uniform(400, 600)
            vx, vy = pygame.Vector2(speed, 0).rotate_rad(angle)

            state.particle_system.particles.append(Particle(
                x=pos[0], y=pos[1],
                vx=vx, vy=vy,
                lifetime=0.3,
                max_lifetime=0.3,
                color=self._color_secondary,
                size=random.uniform(3, 5)
            ))