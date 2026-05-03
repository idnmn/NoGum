import pygame
from abc import ABC, abstractmethod

# отделение графики от хитбоксов для t-d отрисовки
class Renderable(ABC):
    # возвращает физический хитбокс
    @property
    @abstractmethod
    def rect(self) -> pygame.Rect:
        pass

    # метод отрисовки
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        pass