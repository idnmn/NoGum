import pygame
import math
from configs import config
import random
from pygame import Vector2
from models.collidable import CollisionBody
from models.enemies import Enemy
from models.game_state import GameState


class Projectile():
    def __init__(self, state: GameState, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0) -> None:
        self._state = state
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"projectile"}
        )
        self.velocity = velocity
        self.damage = damage
        self.lifetime = lifetime
        self.is_active = True
        self.penetrating_count = 0
        self.penetrating_counter = 0

        self.hitted_enemies = set()

    def update(self, dt: float) -> None:
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt
        self.lifetime -= dt

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def enemy_impact(self, pos: tuple[float, float], enemy: Enemy) -> None:
        self._state.particle_system.spawn_enemy_impact(pos, color=enemy.impact_color)

    def wall_impact(self, pos: tuple[float, float]):
        distance = Vector2((self._state.player.rect.centerx - pos[0],
                            self._state.player.rect.centery - pos[1])).magnitude()
        ratio = (1200 - distance) * 0.0015
        if ratio <= 0:
            ratio = 0

        self._state.particle_system.spawn_wall_impact(pos,
                                                      color=config.MINIMAP_WALL_COLOR_LIST[self._state.level_seed - 1])
        self._state.camera.shake(config.IMPACT_SHAKE_AMOUNT * ratio, config.IMPACT_SHAKE_DURATION)

        self._state.audio_manager.play_sound(f'wall_impact_{random.randint(1, 4)}', ratio)


class PointerProjectile(Projectile):
    def __init__(self, state: GameState, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0) -> None:
        super().__init__(state, x, y, size, velocity, damage, lifetime)
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"projectile", "player_owner"}
        )

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (110, 190, 130), self.rect.center, self.rect.width // 2)
        pygame.draw.circle(surface, (155, 255, 135), self.rect.center, (self.rect.width // 2) * 0.8)

    def enemy_impact(self, pos: tuple[float, float], enemy: Enemy) -> None:
        super().enemy_impact(pos, enemy)
        enemy.take_damage(self.damage)


class TazerProjectile(Projectile):
    def __init__(self, state: GameState, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0) -> None:
        super().__init__(state, x, y, size, velocity, damage, lifetime)
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"projectile", "player_owner"}
        )

        self._time_param = random.uniform(-90, 90)
        self.penetrating_count = 1

    def update(self, dt: float) -> None:
        self._time_param += dt * 20
        self._time_param = self._time_param % 360

        offset_vector = (self.velocity.normalize().rotate(90) * (5 + (self.velocity.magnitude() / 70))
                         ** 0.5 * math.cos(self._time_param))

        self.rect.x += self.velocity.x * dt + offset_vector.x
        self.rect.y += self.velocity.y * dt + offset_vector.y

        self.lifetime -= dt

        self._state.particle_system.spawn_tazer_projectile(self.body.center)

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (155, 240, 255), self.rect)

    def enemy_impact(self, pos: tuple[float, float], enemy: Enemy) -> None:
        self._state.particle_system.spawn_enemy_impact(pos, color=self._state.weapon.signature_color)
        enemy.take_damage(self.damage)
        enemy.status_manager.electrified += self._state.weapon.electrified_points


class ZapProjectile(Projectile):
    def __init__(self, state: GameState, x: float, y: float, size: int, velocity: pygame.Vector2 | None = None,
                 damage: float = 0.0, lifetime: float = 0.0, stun_time = 0, electrified = 0) -> None:
        super().__init__(state, x, y, size, velocity, damage, lifetime)
        self.body = CollisionBody(
            rect=pygame.Rect((x - size / 2), (y - size / 2), size, size),
            layer="dynamic",
            tags={"projectile", "player_owner"}
        )
        self.penetrating_count = 100

        self.electrified = electrified
        self.stun_time = stun_time

    def update(self, dt: float) -> None:
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        self.lifetime -= dt

        self._state.particle_system.spawn_zap_projectile_trail(self.body.center, self.velocity.normalize())

    def render(self, surface: pygame.Surface) -> None:
        self._state.particle_system.spawn_zap_projectile(self.body.center, self.velocity.normalize())

    def enemy_impact(self, pos: tuple[float, float], enemy: Enemy) -> None:
        self._state.particle_system.spawn_enemy_impact(pos, color=self._state.weapon.signature_color)
        enemy.status_manager.electrified += self.electrified
        enemy._state_timer = self.stun_time
        enemy.state = 'stun'

