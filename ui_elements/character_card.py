import pygame
import json
from pygame import Vector2
from core import utils
from models.game_state import GameState
from ui_elements.button import Button


class CharacterCard:
    def __init__(self, state: GameState, character_name, screen_w: int, screen_h: int):
        self._state = state
        self._screen_w = screen_w
        self._screen_h = screen_h
        self.rect = pygame.Rect(
            (self._screen_w - 500) // 2,
            (self._screen_h - 550) // 2,
            500, 550
        )

        self.character_name = character_name
        self.preview = pygame.image.load(utils.get_resource_path(
            f"assets\\characters\\{self.character_name}_preview.png"))
        self.preview = pygame.transform.scale(self.preview, (240, 130))

        self.speed_icon = pygame.image.load(utils.get_resource_path(f"assets\\hud\\speed_icon.png"))
        self.hp_icon = pygame.image.load(utils.get_resource_path(f"assets\\hud\\hp_icon.png"))

        file = utils.get_resource_path(f"characters_stats\\{self.character_name}.json")
        with open(file, "r", encoding="utf-8") as f:
            self.character_config = json.load(f)

        self.start_button = Button(
            title="Start >",
            x=self.rect.x + self.rect.width - 170,
            y=self.rect.y + self.rect.height - 65,
            width=150,
            height=45,
            is_active=True,
            action=lambda: (setattr(self._state, "character", self.character_name),
                            self._state.menu_screens['main_menu'].start_game())
        )

    def resize(self, screen_w: int, screen_h: int):
        self._screen_w = screen_w
        self._screen_h = screen_h
        self.rect.x, self.rect.y = (self._screen_w - 500) // 2, (self._screen_h - 550) // 2,
        self.start_button.change_position(self.rect.x + self.rect.width - 170, self.rect.y + self.rect.height - 65)

    def update(self, dt: float, mouse_pos: Vector2, events: list[pygame.event.Event]) -> None:
        self._handle_events(events)
        self.start_button.update(dt, mouse_pos, self._state)

    def _handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self._state.is_running = False

            # нажатия кнопок
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.start_button.state == 'selected':
                    self.start_button.click()
                    break

    def render(self, surface: pygame.Surface):
        w, h = self.rect.width, self.rect.height
        x = self.rect.x
        y = self.rect.y
        pygame.draw.rect(surface, (25, 25, 35), (x + 2, y + 2, w - 4, h - 4), border_radius=10)
        pygame.draw.rect(surface, (60, 60, 85), (x, y, w, h), 2, border_radius=10)

        font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 36)
        title = font.render(self.character_name.capitalize(), True, (220, 220, 220))
        title_x, title_y =  self.rect.x + (self.rect.width - title.get_width()) // 2, self.rect.y + 20
        surface.blit(title, (title_x, title_y))

        prev_x, prev_y = self.rect.x + (self.rect.width - self.preview.get_width()) // 2, self.rect.y + 60
        surface.blit(self.preview, (prev_x, prev_y))

        font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 22)
        start_y = self.rect.y + self.preview.get_height() + 80
        for i, text in enumerate(self.character_config['description']):
            surface.blit(font.render(text, True, (220, 220, 220)), (self.rect.x + 30,
                                                                    self.rect.y + start_y + i * 20))

        font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 36)
        hp_x = self.rect.x + self.rect.width // 2 - 140
        hp = font.render(str(self.character_config['max_hp']), True, (220, 220, 220))
        surface.blit(self.hp_icon, (hp_x, start_y))
        surface.blit(hp, (hp_x + 45, start_y))

        speed_x = self.rect.x + self.rect.width // 2 + 30
        speed = font.render(str(self.character_config['max_speed']), True, (220, 220, 220))
        surface.blit(self.speed_icon, (speed_x, start_y))
        surface.blit(speed, (speed_x + 45, start_y))

        self.start_button.render(surface)
