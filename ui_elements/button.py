import pygame
from pygame import Vector2

import config
from models.game_state import GameState


# кнопка
class Button:
    def __init__(self, title: str, x: float, y: float, width: float, height: float,
                 is_active: bool, action: callable, args: list[object] = []) -> None:
        self.interactive_hitbox = pygame.rect.Rect(x, y, width, height)
        self._title = title

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.state: str = 'active' if is_active else 'inactive' # active, selected, clicked, inactive
        self.is_active = is_active
        self._action = action
        self._args = args

        self._font = pygame.font.Font("assets/QBF_font.ttf", 28)

        self._clicked_timer = 0.0

        self._need_sound = True

    def change_position(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.interactive_hitbox = pygame.rect.Rect(x, y, self.width, self.height)

    # обновляем состояние
    def update(self, dt: float, mouse_pos: Vector2, state: GameState) -> None:
        if not self.state == 'clicked':
            if self.interactive_hitbox.collidepoint(mouse_pos) and self.is_active:
                self.state = 'selected'

                if self._need_sound:
                    self._need_sound = False
                    state.audio_manager.play_sound('ui_selected')
            else:
                self.state = 'active' if self.is_active else 'inactive'
                self._need_sound = True

        if self.state == 'clicked':
            self._clicked_timer -= dt

            if self._clicked_timer < 0:
                self.state = 'active' if self.is_active else 'inactive'

    def render(self, surface: pygame.Surface) -> None:
        # отрисовываем активную кнопку
        if self.state == 'active':
            color_inside = config.BUTTON_ACTIVE_COLOR_INSIDE
            color_outside = config.BUTTON_ACTIVE_COLOR_OUTSIDE
            button_color = (220, 220, 220)
        elif self.state == 'selected':
            color_inside = config.BUTTON_SELECTED_COLOR_INSIDE
            color_outside = config.BUTTON_SELECTED_COLOR_OUTSIDE
            button_color = color_outside
        elif self.state == 'clicked':
            color_inside = config.BUTTON_CLICKED_COLOR_INSIDE
            color_outside = config.BUTTON_CLICKED_COLOR_OUTSIDE
            button_color = color_outside
        else:
            color_inside = config.BUTTON_INACTIVE_COLOR_INSIDE
            color_outside = config.BUTTON_INACTIVE_COLOR_OUTSIDE
            button_color = color_outside

        title = self._font.render(f"{self._title}",
                                  True, button_color)
        title_x = (self.width - title.get_width()) / 2
        title_y = (self.height - title.get_height()) / 2

        pygame.draw.rect(surface, color_outside, self.interactive_hitbox, border_radius=5)
        pygame.draw.rect(surface, color_inside,
                         (self.x + 4, self.y + 4, self.width - 8, self.height - 8), border_radius=5)
        surface.blit(title, (self.x + title_x, self.y + title_y))

    def click(self):
        self.state = 'clicked'
        self._clicked_timer = config.BUTTON_CLICKED_TIME
        self._action(*self._args)


# особые кнопки для меню
class MenuButton(Button):
    def __init__(self, title: str, x: float, y: float, width: float, height: float,
                 is_active: bool, action: callable, args: list[object] = [], uncentred: bool = False) -> None:
        super().__init__(title, x, y, width, height, is_active, action, args)
        self._font = pygame.font.Font("assets/QBF_font.ttf", 34)
        self._selected_font = pygame.font.Font("assets/QBF_font.ttf", 38)

        self.width = self._selected_font.render(self._title,True, (0, 0, 0)).get_width()
        self.interactive_hitbox = pygame.rect.Rect(x, y, self.width, height)

        self.uncentred = uncentred

    def render(self, surface: pygame.Surface) -> None:
        # отрисовываем активную кнопку
        if self.state == 'active':
            button_color = config.MENU_BUTTON_ACTIVE_COLOR
            font = self._font
        elif self.state == 'selected':
            button_color = config.MENU_BUTTON_SELECTED_COLOR
            font = self._selected_font
        elif self.state == 'clicked':
            button_color = config.MENU_BUTTON_CLICKED_COLOR
            font = self._font
        else:
            button_color = config.BUTTON_INACTIVE_COLOR_OUTSIDE
            font = self._font

        title = font.render(self._title,True, button_color)
        if not self.uncentred:
            title_x = (self.width - title.get_width()) / 2
            title_y = (self.height - title.get_height()) / 2
        else:
            title_x = 0
            title_y = 0

        surface.blit(title, (self.x + title_x, self.y + title_y))