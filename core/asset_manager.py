import pygame
import os
import config
from core import utils

# подгрузчик спрайтов
class AssetManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def load_sprite(self, filename: str, target_size: tuple[int, int] | None = None) -> pygame.Surface:
        path = utils.get_resource_path(os.path.join("assets", filename))
        if path not in self._cache:
            try:
                img = pygame.image.load(path).convert_alpha()
                if target_size:
                    img = pygame.transform.scale(img, target_size)
                self._cache[path] = img
            except pygame.error:
                # Fallback: если файл не найден создаём квадрат
                size = target_size or (config.TILE_SIZE, config.TILE_SIZE)
                img = pygame.Surface(size, pygame.SRCALPHA)
                img.fill((100, 100, 100))
                self._cache[path] = img
        return self._cache[path]