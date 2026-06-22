import pygame
import os
import config
from core.music_crossfade_system import CrossfadeMusicSystem
from core import utils
from models.game_state import GameState


class AudioManager:
    _instance = None

    def __new__(cls, state: GameState):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, state: GameState) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._state = state

        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self.sound_volume = 0.8
        self.music_volume = 0.7
        self.master_volume = 1.0

        self.crossfade_system = None

        self._load_all_sounds()

    # грузим все звуки
    def _load_all_sounds(self) -> None:
        sounds_dir = utils.get_resource_path(os.path.join(config.ASSETS_DIR, "sounds"))

        sound_mapping = {
            "dash": "skills/dash.wav",
            'slash_hit': 'skills/slash_hit.wav',
            'slash': 'skills/slash.wav',
            'skill_reloaded': 'skills/reloaded.wav',
            'skill_get_charge': 'skills/get_charge.wav',

            "mommy_explode": "enemies/mommy_explode.wav",
            "mommy_pre_explode": "enemies/mommy_pre_explode.wav",
            'bookworm_step_1': 'enemies/bookworm_step_1.wav',
            'bookworm_step_2': 'enemies/bookworm_step_2.wav',
            'bookworm_step_3': 'enemies/bookworm_step_3.wav',
            'bookworm_step_4': 'enemies/bookworm_step_4.wav',
            'bookworm_death_1': 'enemies/bookworm_death_1.wav',
            'bookworm_death_2': 'enemies/bookworm_death_2.wav',
            'bookworm_death_3': 'enemies/bookworm_death_3.wav',
            'bookworm_death_4': 'enemies/bookworm_death_4.wav',
            'bookworm_damaged_1': 'enemies/bookworm_damaged_1.wav',
            'bookworm_damaged_2': 'enemies/bookworm_damaged_2.wav',
            'bookworm_damaged_3': 'enemies/bookworm_damaged_3.wav',
            'bookworm_damaged_4': 'enemies/bookworm_damaged_4.wav',
            'bookworm_dash_1': 'enemies/bookworm_dash_1.wav',
            'bookworm_dash_2': 'enemies/bookworm_dash_2.wav',
            'bookworm_dash_3': 'enemies/bookworm_dash_3.wav',

            "energy_cell_collected_1": 'ui/energy_cell_collected_1.wav',
            "energy_cell_collected_2": 'ui/energy_cell_collected_2.wav',
            "energy_cell_collected_3": 'ui/energy_cell_collected_3.wav',
            "energy_cell_collected_4": 'ui/energy_cell_collected_4.wav',
            "scrap_collected_1": 'ui/scrap_collected_1.wav',
            "scrap_collected_2": 'ui/scrap_collected_2.wav',
            "scrap_collected_3": 'ui/scrap_collected_3.wav',
            "scrap_collected_4": 'ui/scrap_collected_4.wav',
            'bonus_collected': 'ui/bonus_collected.wav',
            'terminal_close': 'ui/terminal_close.wav',
            'terminal_open': 'ui/terminal_open.wav',
            'terminal_select': 'ui/terminal_selected.wav',
            'ui_open': 'ui/ui_open.wav',
            'ui_close': 'ui/ui_close.wav',
            'ui_selected': 'ui/ui_selected.wav',
            'teleported': 'ui/teleported.wav',
            'weapon_upgrade': 'ui/weapon_upgrade.wav',
            'chest_open': 'ui/chest_open.wav',
            'wall_impact_1': 'ui/wall_impact_1.wav',
            'wall_impact_2': 'ui/wall_impact_2.wav',
            'wall_impact_3': 'ui/wall_impact_3.wav',
            'wall_impact_4': 'ui/wall_impact_4.wav',
            'door_close': 'ui/door_close.wav',

            'player_walk': 'player/walk.wav',
            'player_damaged_1': 'player/damaged_1.wav',
            'player_damaged_2': 'player/damaged_2.wav',
            'player_damaged_3': 'player/damaged_3.wav',

            'pointer_shot': 'weapons/pointer/shot.wav',
            'pointer_reload': 'weapons/pointer/reload.wav',
            'pointer_reload_end': 'weapons/pointer/reload_end.wav'
        }

        for sound, filename in sound_mapping.items():
            path = utils.get_resource_path(os.path.join(sounds_dir, filename))

            if os.path.exists(path):
                try:
                    self._sounds[sound] = pygame.mixer.Sound(path)
                    self._sounds[sound].set_volume(self.sound_volume)
                except pygame.error as e:
                    print(f"не удалось загрузить звук {filename}: {e}")
            else:
                # заглушка
                self._sounds[sound] = pygame.mixer.Sound(buffer=bytes(1024))

    # воспроизведение звука
    def play_sound(self, name: str, volume: float=1.0, loops: int = 0) -> None:
        if name in self._sounds:
            sound = self._sounds[name]
            sound.set_volume(min(self.sound_volume * self.master_volume * 0.4 * volume, 1.0))
            sound.play(loops=loops)

    # воспроизведение музыки
    def play_music(self, track_name: str) -> None:
        music_path = utils.get_resource_path(os.path.join(config.ASSETS_DIR, "music", track_name + '.wav'))
        muted_path = utils.get_resource_path(os.path.join(config.ASSETS_DIR, "music", track_name + '_muted.wav'))

        self.crossfade_system = CrossfadeMusicSystem(self._state, music_path, muted_path, 0.3)

    # стоп музыка
    def stop_music(self) -> None:
        self.crossfade_system.stop_music()

    def set_sound_volume(self, volume: float) -> None:
        volume /= 100.0

        self.sound_volume = volume
        for sound in self._sounds.values():
            sound.set_volume(volume * self.master_volume)

    def set_music_volume(self, volume: float) -> None:
        volume /= 100.0

        self.music_volume = volume
        self.crossfade_system.set_volume(volume * self.master_volume)

    def set_master_volume(self, volume: float) -> None:
        volume /= 100.0

        self.master_volume = volume
        self.crossfade_system.set_volume(volume * self.music_volume)
        for sound in self._sounds.values():
            sound.set_volume(volume * self.sound_volume)
