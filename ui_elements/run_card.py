import pygame
import json
import os
from pygame import Vector2
from core import utils
from models.game_state import GameState
from ui_elements.button import Button


class RunCard:
    def __init__(self, state: GameState, run_name, screen_w: int, screen_h: int):
        self._state = state
        self._screen_w = screen_w
        self._screen_h = screen_h
        self.rect = pygame.Rect(
            (self._screen_w - 500) // 2,
            (self._screen_h - 550) // 2,
            500, 550
        )

        self.run = run_name
        self.preview = pygame.image.load(utils.get_resource_path(
            f"runs/screenshots/{run_name[:-5]}_screenshot.png"))
        self.preview = pygame.transform.scale(self.preview, (144, 144))

        file = utils.get_resource_path(f"runs/{self.run}")
        with open(file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        date = self.run[4:-5].replace("_", "")
        self.data['Play date'] = f'{date[:2]}.{date[2:4]}.{date[4:6]}-{date[6:8]}:{date[8:10]}'
        del self.data["_date_time"]

        play_time = self.data["_play_time"]
        mins = int(play_time // 60)
        secs = int(play_time % 60)
        self.data['playtime'] = f"{mins:02d}:{secs:02d}"
        del self.data["_play_time"]

        self.delete_button = Button(
            title="Delete",
            x=self.rect.x + self.rect.width - 170,
            y=self.rect.y + self.rect.height - 65,
            width=150,
            height=45,
            is_active=True,
            action=lambda: (os.remove(utils.get_resource_path(f"runs/{self.run}")),
                            os.remove(utils.get_resource_path(f"runs/screenshots/{self.run[:-5]}_screenshot.png")),
                            self._state.menu_manager.active_screen.reinit(),),
        )

    def resize(self, screen_w: int, screen_h: int):
        self._screen_w = screen_w
        self._screen_h = screen_h
        self.rect.x, self.rect.y = (self._screen_w - 500) // 2, (self._screen_h - 550) // 2,
        self.delete_button.change_position(self.rect.x + self.rect.width - 170, self.rect.y + self.rect.height - 65)

    def update(self, dt: float, mouse_pos: Vector2, events: list[pygame.event.Event]) -> None:
        self._handle_events(events)
        self.delete_button.update(dt, mouse_pos, self._state)

    def _handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self._state.is_running = False

            # нажатия кнопок
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.delete_button.state == 'selected':
                    self.delete_button.click()
                    break

    def render(self, surface: pygame.Surface):
        w, h = self.rect.width, self.rect.height
        x = self.rect.x
        y = self.rect.y
        pygame.draw.rect(surface, (25, 25, 35), (x + 2, y + 2, w - 4, h - 4), border_radius=10)
        pygame.draw.rect(surface, (60, 60, 85), (x, y, w, h), 2, border_radius=10)

        font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 36)
        title = font.render(self.data['character'].capitalize(), True, (220, 220, 220))
        title_x, title_y =  self.rect.x + (self.rect.width - title.get_width()) // 2, self.rect.y + 20
        surface.blit(title, (title_x, title_y))

        prev_x, prev_y = self.rect.x + (self.rect.width - self.preview.get_width()) // 2, self.rect.y + 60
        surface.blit(self.preview, (prev_x, prev_y))

        font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 22)
        start_y = self.rect.y + self.preview.get_height() - 40
        for i,(key, value) in list(enumerate(self.data.items()))[1:]:
            if key != 'inventory':
                surface.blit(font.render(f'{key.replace('_', ' ').capitalize()}: {value}',
                                         True, (220, 220, 220)), (self.rect.x + 30,
                                                                  self.rect.y + start_y + i * 30))

            else:
                for j, (item, count) in list(enumerate(self.data[key].items())):
                    source = self._state.assets[item.lower()]
                    w, h = source.get_width(), source.get_height()
                    sprite = pygame.transform.scale(source, (w * 0.5, h * 0.5))

                    surface.blit(sprite, (self.rect.x + 60 * (j + 1),
                                                              self.rect.y + start_y + i * 30))
                    surface.blit(font.render(f'{count}',
                                             True, (220, 220, 220)),
                                        (self.rect.x + 60 * (j + 1) + w * 0.5 + 3, self.rect.y + start_y + i * 30))



        #
        # font = pygame.font.Font(utils.get_resource_path("assets/QBF_font.ttf"), 36)
        # hp_x = self.rect.x + self.rect.width // 2 - 140
        # hp = font.render(str(self.character_config['max_hp']), True, (220, 220, 220))
        # surface.blit(self.hp_icon, (hp_x, start_y))
        # surface.blit(hp, (hp_x + 45, start_y))
        #
        # speed_x = self.rect.x + self.rect.width // 2 + 30
        # speed = font.render(str(self.character_config['max_speed']), True, (220, 220, 220))
        # surface.blit(self.speed_icon, (speed_x, start_y))
        # surface.blit(speed, (speed_x + 45, start_y))

        self.delete_button.render(surface)
