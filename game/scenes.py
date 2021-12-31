from __future__ import annotations

import pygame as pg

from . import BaseScene, game, assets
import data_structure as ds


# PLAY X, Y = 90, 550
# QUIT X, Y = 420, 550
# SIZE X, Y = 300, 100

class MainMenuScene(BaseScene):
    def update(self):
        for ev in self.get_events():
            if ev.type == pg.MOUSEBUTTONUP:
                if assets.menu.play_rect.collidepoint(*ev.pos):
                    self.manager.spawn_scene(PlayScene)
                elif assets.menu.quit_rect.collidepoint(*ev.pos):
                    game.stop()

    def draw(self, surface: pg.Surface):
        surface.blit(assets.menu.background, (0, 0))


class PlayScene(BaseScene):
    world: ds.World

    def init(self, *args, **kwargs):
        self.world = ds.World(assets.game.entry_map)

    def update(self):
        pass

    def draw(self, surface: pg.Surface):
        pass
