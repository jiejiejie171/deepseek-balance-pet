import os
from contextlib import suppress
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame
except ImportError:  # pragma: no cover - optional at runtime
    pygame = None

CHANNELS = 8


class SoundPlayer:
    """Play the upstream duck click sound on every click.

    SDL's mixer (via pygame) follows the current system output device and gives
    each rapid click its own channel, so repeated clicks do not go silent.
    """

    def __init__(self, assets: Path, enabled: bool = True):
        self.enabled = enabled
        self._sound = None
        self._channels = []
        self._next = 0
        if pygame is None:
            return
        with suppress(Exception):
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=256)
            pygame.mixer.set_num_channels(CHANNELS)
            self._sound = pygame.mixer.Sound(str(assets / "Ya1.wav"))
            self._channels = [pygame.mixer.Channel(i) for i in range(CHANNELS)]

    def play_click(self) -> None:
        if not self.enabled or self._sound is None or not self._channels:
            return
        with suppress(Exception):
            channel = self._channels[self._next]
            self._next = (self._next + 1) % len(self._channels)
            channel.play(self._sound)
