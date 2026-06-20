import pygame

import config
from skills.skill import Skill


class SkillIndicator:
    def __init__(self, x: float, y: float, skill: Skill):
        self.rect = pygame.Rect(x, y, 70, 80)
        self.skill = skill

        self.sprite = skill.indicator_sprite
        self.sprite_x = (self.rect.width - self.sprite.get_width()) / 2
        self.sprite_y = (self.rect.height - 10 - self.sprite.get_height()) / 2
        self.x = x
        self.y = y

        self._alpha = 180

    def render(self, surface: pygame.Surface):
        if self.skill.charges_count == self.skill.max_charges:
            color = config.BUTTON_ACTIVE_COLOR_INSIDE
        else:
            color = config.BUTTON_INACTIVE_COLOR_INSIDE
        fill_color = config.BUTTON_INACTIVE_COLOR_OUTSIDE

        render_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        pygame.draw.rect(render_surface, color,
                         (0, 0, self.rect.width, self.rect.height - 10))

        render_sprite = self.sprite.copy()
        render_sprite.set_alpha(self._alpha)

        if not self.skill.charges_count == self.skill.max_charges and not self.skill.is_using:
            height = self.rect.height * self.skill.cooldown_ratio
            pygame.draw.rect(render_surface, fill_color,
                             (0, self.rect.height - 10 - height + 1, self.rect.width, height))

            render_sprite.fill((150, 150, 150, 200), None, pygame.BLEND_RGBA_MULT)

        render_surface.blit(render_sprite, (self.sprite_x, self.sprite_y))

        # отрисовываем заряды скилла
        if self.skill.max_charges > 1:
            charge_color_active = (220, 220, 220)
            charge_color_inactive = (100, 100, 100)

            charge_w = 70 / self.skill.max_charges - ((self.skill.max_charges - 1) * 2) / self.skill.max_charges
            for i in range(self.skill.charges_count):
                pygame.draw.rect(surface, charge_color_active, (self.x + (charge_w + 2) * i,
                                                                       self.y + 72,
                                                                       charge_w,
                                                                       5))

            for i in range(self.skill.charges_count, self.skill.max_charges):
                pygame.draw.rect(surface, charge_color_inactive, (self.x + (charge_w + 2) * i,
                                                                       self.y + 72,
                                                                       charge_w,
                                                                       5))

        render_surface.set_alpha(self._alpha)
        surface.blit(render_surface, (self.x, self.y))