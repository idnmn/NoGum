import pygame

import config
from skills.skill import Skill


class SkillIndicator:
    def __init__(self, x: float, y: float, skill: Skill):
        self.rect = pygame.Rect(x, y, 70, 70)
        self.skill = skill

        self.sprite = skill.indicator_sprite
        self.sprite_x = (self.rect.width - self.sprite.get_width()) / 2
        self.sprite_y = (self.rect.height - self.sprite.get_height()) / 2
        self.x = x
        self.y = y

        self._alpha = 180

    def render(self, surface: pygame.Surface):
        if self.skill.is_ready:
            color = config.BUTTON_ACTIVE_COLOR_INSIDE
        else:
            fill_color = config.BUTTON_INACTIVE_COLOR_OUTSIDE
            color = config.BUTTON_INACTIVE_COLOR_INSIDE


        render_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        pygame.draw.rect(render_surface, color,
                         (0, 0, self.rect.width, self.rect.height))

        render_sprite = self.sprite.copy()
        render_sprite.set_alpha(self._alpha)

        if not self.skill.is_ready:
            height = self.rect.height * self.skill.cooldown_ratio
            pygame.draw.rect(render_surface, fill_color,
                             (0, self.rect.height - height + 1, self.rect.width, height))

            render_sprite.fill((150, 150, 150, 200), None, pygame.BLEND_RGBA_MULT)

        render_surface.blit(render_sprite, (self.sprite_x, self.sprite_y))

        render_surface.set_alpha(self._alpha)
        surface.blit(render_surface, (self.x, self.y))