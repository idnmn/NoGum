import pygame
import random
from configs import config
import os
from core import utils
from models.game_state import GameState


class CrossfadeMusicSystem:
    def __init__(self, state: GameState, normal_path: str, muted_path: str, fade_duration: float = 1.0) -> None:
        self._state = state

        self.normal_sound = pygame.mixer.Sound(normal_path)
        self.muted_sound = pygame.mixer.Sound(muted_path)

        self.volume = self._state.audio_manager.music_volume * self._state.audio_manager.master_volume

        # запускаем обе дорожки на отдельных каналах синхронно
        self.ch_normal = self.normal_sound.play()
        self.ch_muted = self.muted_sound.play()

        # Начальные громкости: 100% обычная, 0% приглушенная
        self.ch_normal.set_volume(1.0 * self.volume)
        self.ch_muted.set_volume(0.0)

        # параметры фейда
        self._fade_duration = fade_duration
        self._target_mix = 1.0
        self._current_mix = 1.0
        self._fade_timer = 0.0
        self._fade_start_mix = 0.0

        self._track_duration = self.normal_sound.get_length()
        self._track_swap_timer = 0.0

        self._music_list = ['astra', 'acid_rain', 'black_bees']
        self._active_track = normal_path[:-4].split('\\')[-1]

    def update(self, dt: float) -> None:
        self._track_swap_timer += dt
        if self._track_swap_timer >= self._track_duration:
            next_track = random.choice([track for track in self._music_list if track != self._active_track])
            normal_path, muted_path = self._get_path(next_track)

            self.stop()

            self.normal_sound = pygame.mixer.Sound(utils.get_resource_path(normal_path))
            self.muted_sound = pygame.mixer.Sound(utils.get_resource_path(muted_path))

            # запускаем обе дорожки на отдельных каналах синхронно
            self.ch_normal = self.normal_sound.play()
            self.ch_muted = self.muted_sound.play()
            self.ch_normal.set_volume(self._current_mix * self.volume)
            self.ch_muted.set_volume((1.0 - self._current_mix) * self.volume)
            self._active_track = normal_path[:-4].split('\\')[-1]

            self._track_duration = self.normal_sound.get_length()
            self._track_swap_timer = 0.0

        if abs(self._current_mix - self._target_mix) < 0.001:
            return

        self._fade_timer += dt

        if self._fade_timer >= self._fade_duration:
            return

        progress = min(self._fade_timer / self._fade_duration, 1.0)

        if self._target_mix > self._current_mix:
            self._current_mix = self._fade_start_mix + progress * (self._target_mix - self._fade_start_mix)
        else:
            self._current_mix = self._fade_start_mix - progress * (self._fade_start_mix - self._target_mix)

        # Применяем к каналам
        self.ch_normal.set_volume(self._current_mix * self.volume)
        self.ch_muted.set_volume((1.0 - self._current_mix) * self.volume)

        if progress >= 1.0:
            self._current_mix = self._target_mix

    def _get_path(self, track: str) -> tuple:
        music_path = os.path.join(config.ASSETS_DIR, "music", track + '.wav')
        muted_path = os.path.join(config.ASSETS_DIR, "music", track + '_muted.wav')

        return music_path, muted_path

    def set_muted(self, is_muted: bool) -> None:
        self._target_mix = 0.0 if is_muted else 1.0
        self._fade_start_mix = self._current_mix
        self._fade_timer = 0

    def stop(self) -> None:
        self.ch_normal.stop()
        self.ch_muted.stop()

    def set_volume(self, volume) -> None:
        self.volume = volume
        self.ch_normal.set_volume(self._current_mix * self.volume)
        self.ch_muted.set_volume((1.0 - self._current_mix) * self.volume)
