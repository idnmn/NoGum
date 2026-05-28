from models.game_state import GameState
from models.collectable import Collectable


class CollectableSystem:
    def __init__(self, state: GameState) -> None:
        self._state = state

        self.items: list[Collectable] = []

    def update(self, dt: float) -> None:
        active_room = self._state.room_manager.active_room
        obstacles = active_room.walls
        if active_room.terminal:
            obstacles.append(active_room.terminal)

        for item in self.items:
            item.update(dt, self._state.player)

            # смэрть от старости
            if item.lifetime < 0:
                item.is_active = False
                continue

            # коллизия со стенами только активной комнаты
            self._state.collision_system.resolve_obstacles(item, obstacles)

            # подбор игроком
            if item.rect.colliderect(self._state.player.rect):
                item.is_active = False
                item.collect(self._state)
                item.spawn_particles(self._state)

        # очищаем неактивные
        self.items = [item for item in self.items if item.is_active]


