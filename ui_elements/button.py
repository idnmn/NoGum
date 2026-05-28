import pygame

import config


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

    # обновляем таймер
    def update(self, dt: float) -> None:
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