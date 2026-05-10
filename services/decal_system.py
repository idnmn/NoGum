import pygame
from models.decal import Decal

class DecalSystem:
    def __init__(self) -> None:
        self.decals: list[Decal] = []

    def update(self, dt: float) -> None:
        for decal in self.decals:
            decal.update(dt)

        self.decals = [d for d in self.decals if d.life_timer > 0 or d.lifetime == -1]

    def clear(self) -> None:
        self.decals = []