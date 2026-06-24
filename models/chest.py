from models.collectable import *
from models.collidable import CollisionBody
from models.game_state import GameState


# сундук для рун.... РУНДУК
# сундук для бустеров.... БУРУНДУК
class Chest():
    def __init__(self, x: float, y: float, size: int,
                 sprite_closed: pygame.Surface, sprite_opened: pygame.Surface) -> None:
        self.body = CollisionBody(
            rect=pygame.Rect(x, y, size, size),
            layer="static",
            tags={"chest"}
        )

        self.interactive_hitbox = CollisionBody(
            rect=pygame.Rect(x - size * 0.5, y - size * 0.5, size * 2, size * 2),
            layer="interactive",
            tags={"chest"}
        )
        self.body.shadow_offset = -10

        self.sprite_closed = sprite_closed.copy().convert_alpha()
        self.near_player_sprite = sprite_closed.copy()
        self.near_player_sprite.fill((0, 30, 0, 0), None, pygame.BLEND_RGB_ADD)
        self.sprite_opened = sprite_opened.copy().convert_alpha()
        self.visual_offset_y = -(sprite_closed.get_height() - size)
        self.visual_offset_x = -(sprite_closed.get_width() - size) / 2

        self.is_closed = True
        self.is_near_player = False

        self._magnet_timer = 1.0
        self._timer_flag = False

    @property
    def rect(self) -> pygame.Rect:
        return self.body.rect

    def render(self, surface: pygame.Surface) -> None:
        draw_x = self.rect.x + self.visual_offset_x
        draw_y = self.rect.y + self.visual_offset_y

        # меняем спрайт если роядом игрок
        if self.is_closed:
            if self.is_near_player:
                near_player_sprite = self.sprite_closed.copy()
                near_player_sprite.fill((0, 30, 0, 0), None, pygame.BLEND_RGB_ADD)

            elif not self.is_near_player:
                self.sprite_closed = self.sprite_closed.copy()

        # отрисовываем спрайт
        if self.is_closed:
            if self.is_near_player:
                sprite = self.near_player_sprite
            else:
                sprite = self.sprite_closed
        else:
            sprite = self.sprite_opened
        surface.blit(sprite, (draw_x, draw_y))

    def update(self, dt: float, state: GameState) -> None:
        if self.is_closed:
            return

        if not self._timer_flag:
            self._magnet_timer -= dt

            if self._magnet_timer <= 0:
                for item in state.collectable_system.items:
                    if item.name == '':
                        item.magnet = True
                self._timer_flag = True

    def open(self, state: GameState) -> None:
        self.is_closed = False
        self.visual_offset_y = -(self.sprite_opened.get_height() - self.rect.height)

        dir_to_player = -(Vector2(state.player.rect.center) - Vector2(self.rect.center)).normalize()
        angle = 60
        state.camera.shake(25, 0.1)


        # спавним дроп
        if state.drop_pool:
            # с шансом 20% два предмета
            if random.randint(1, 100) <= 20:
                drop_items = random.choices(state.drop_pool, k=2)
            else:
                drop_items = [random.choice(state.drop_pool)]

            for item in drop_items:
                velocity = 1000 * dir_to_player.rotate(random.uniform(-angle, angle))
                state.collectable_system.items.append(item[0](
                    x=self.rect.centerx,
                    y=self.rect.centery,
                    size=35,
                    lifetime=15,
                    max_speed=1000,
                    vx=velocity.x,
                    vy=velocity.y,
                    acceleration=-5,
                    magnet=False,
                    collect_range=300,
                    sprite=state.assets[item[1]],
                ))


        if state.player.hp != state.player.max_hp:
            for _ in range(random.randint(6, 10)):
                velocity = random.uniform(600, 1000) * dir_to_player.rotate(random.uniform(-angle, angle))
                state.collectable_system.items.append(EnergyCell(
                    x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                    y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                    size=7,
                    lifetime=10,
                    max_speed=600,
                    collect_range=300,
                    vx=velocity.x,
                    vy=velocity.y,
                    acceleration=-3,
                    magnet=False,
                ))

        for _ in range(random.randint(2 * (state.level_number + 1), 3 * (state.level_number + 1))):
            velocity = random.uniform(400, 800) * dir_to_player.rotate(random.uniform(-angle, angle))
            state.collectable_system.items.append(Scrap(
                x=random.uniform(self.rect.x, self.rect.x + self.rect.width),
                y=random.uniform(self.rect.y, self.rect.y + self.rect.height),
                size=15,
                lifetime=10,
                max_speed=300,
                collect_range=300,
                vx=velocity.x,
                vy=velocity.y,
                acceleration=-3,
                magnet=False,
                sprites=state.assets['scrap_sprites']
            ))

        state.particle_system.spawn_open_chest(self.rect.center)
        state.audio_manager.play_sound('chest_open', 1.7)
