from models.collidable import CollisionBody
from models.decal import Decal
from models.shadow import Shadow

class DecalSystem:
    def __init__(self) -> None:
        self.decals: list[Decal] = []
        self.shadows: list[Shadow] = []

        self._limit = 200

    def update(self, dt: float) -> None:
        for decal in self.decals:
            decal.update(dt)

        self.decals = [d for d in self.decals if d.life_timer > 0 or d.lifetime == -1]

        while len(self.decals) > self._limit:
            self.decals.pop(0)

    def update_shadows(self, entities: list[CollisionBody]) -> None:
        # добавляем тени тем, у кого ещё нет
        for entity in entities:
            if not entity.have_shadow:
                shadow = Shadow(entity)
                self.shadows.append(shadow)
                entity.have_shadow = True

        # обновляем тени
        for shadow in self.shadows:
            shadow.update()

        # отсекаем тени без хозяев
        self.shadows = [s for s in self.shadows if s.owner in entities]


    def clear(self) -> None:
        self.decals = []