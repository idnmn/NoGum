import pygame
import os
import config
from core.music_crossfade_system import CrossfadeMusicSystem
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
        self.sound_volume = 1.0
        self.music_volume = 0.0
        self.master_volume = 1.0

        self.crossfade_system = None

        self._load_all_sounds()

    # грузим все звуки
    def _load_all_sounds(self) -> None:
        sounds_dir = os.path.join(config.ASSETS_DIR, "sounds")

        sound_mapping = {
            # "shoot": "shoot.wav",
            # "reload": "reload.wav",
            # "hit": "hit.wav",
            # "enemy_death": "enemy_death.wav",
            # "step": "step.wav",
            # "dash": "dash.wav",
            # "pickup": "pickup.wav",
            # "menu_click": "menu_click.wav",
            # "terminal_open": "terminal_open.wav",
            # "explosion": "explosion.wav"
        }

        for sound, filename in sound_mapping.items():
            path = os.path.join(sounds_dir, filename)

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
    def play_sound(self, name: str, volume: float, loops: int = 0) -> None:
        if name in self._sounds:
            sound = self._sounds[name]
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(self.sound_volume)
            sound.play(loops=loops)

    # воспроизведение музыки
    def play_music(self, track_name: str) -> None:
        music_path = os.path.join(config.ASSETS_DIR, "music", track_name + '.wav')
        muted_path = os.path.join(config.ASSETS_DIR, "music", track_name + '_muted.wav')

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
