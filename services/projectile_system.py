from models.enemies import Enemy
from models.game_state import GameState
from models.projectile import Projectile


class ProjectileSystem:
    def __init__(self, state: GameState) -> None:
        self._state = state
        self.projectiles: list[Projectile] = []

        self._limit = 100

    def update(self, dt: float, enemies: list[Enemy]) -> None:
        for p in self.projectiles:
            p.update(dt)

            if p.lifetime <= 0:
                p.is_active = False
                continue

            # коллизия со стенами только активной комнаты
            active_room = self._state.room_manager.active_room
            if active_room:
                for wall in active_room.walls:
                    if p.rect.colliderect(wall.body.rect):
                        p.is_active = False
                        p.wall_impact((p.rect.centerx, p.rect.centery))
                        break
                terminal = active_room.terminal
                if terminal and p.rect.colliderect(terminal.body.rect):
                    p.is_active = False
                    p.wall_impact((p.rect.centerx, p.rect.centery))
                    break

                chest = active_room.chest
                if chest and p.rect.colliderect(chest.body.rect):
                    p.is_active = False
                    p.wall_impact((p.rect.centerx, p.rect.centery))
                    break

            # коллизия с врагами
            for enemy in enemies:
                if p.rect.colliderect(enemy.body.rect):
                    if enemy not in p.hitted_enemies:
                        p.hitted_enemies.add(enemy)
                        p.penetrating_counter += 1
                        p.enemy_impact((p.rect.centerx, p.rect.centery), enemy)
                    if p.penetrating_counter > p.penetrating_count:
                        p.is_active = False
                    if enemy.take_damage(p.damage):
                        self._state.stattracker.damage_dealt += int(p.damage)

        # очистка неактивных снарядов
        self.projectiles = [p for p in self.projectiles if p.is_active]

        while len(self.projectiles) > self._limit:
            self.projectiles.pop(0)
