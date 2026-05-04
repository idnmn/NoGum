import pygame
from models.projectile import Projectile
from models.weapons import Weapon
from models.room_manager import RoomManager

class ProjectileSystem:
    def __init__(self) -> None:
        self.projectiles: list[Projectile] = []

    def spawn(self, projectile, origin: pygame.Vector2, direction: pygame.Vector2, weapon: Weapon) -> None:
        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)

        size = weapon.get_size()
        speed = weapon.get_speed()

        vel = direction.normalize() * speed

        self.projectiles.append(projectile(x=origin.x, y=origin.y, size=size,
                                           velocity=vel, damage=weapon.damage, lifetime=10.0))

    def update(self, dt: float, room_manager: RoomManager) -> None:
        for p in self.projectiles:
            p.rect.x += p.velocity.x * dt
            p.rect.y += p.velocity.y * dt
            p.lifetime -= dt

            if p.lifetime <= 0:
                p.is_active = False
                continue

            # коллизия со стенами только активной комнаты
            if room_manager.active_room:
                for wall in room_manager.active_room.walls:
                    if p.rect.colliderect(wall.body.rect):
                        p.is_active = False
                        # TODO: Добавить эффект удара/звук
                        break

        # очистка неактивных снарядов
        self.projectiles = [p for p in self.projectiles if p.is_active]