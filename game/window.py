from __future__ import annotations

from typing import Callable
from warnings import warn

import pygame as pg


pg.init()


class GameState:
    def __init__(self, fps: int):
        self.max_fps = fps
        self.clock = pg.time.Clock()
        self.running = True
        self._frame: Callable[[pg.Surface, float], ...] | None = None

    def stop(self):
        self.running = False

    def frame(self, func: Callable[[pg.Surface, float], ...]):
        self._frame = func
        return func

    def run(self):
        while self.running:
            if self._frame is not None:
                ms = self.clock.tick()
                self._frame(window, ms/self.max_fps)  # probably you are missing "window" and "delta_time" arguments
            else:
                warn("Running without specified frame executor")
                break


size = (800, 800)
max_fps = 60
window = pg.display.set_mode(size)
game = GameState(max_fps)

__all__ = [
    "size",
    "max_fps",
    "window",
    "game"
]
