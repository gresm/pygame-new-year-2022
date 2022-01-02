from __future__ import annotations

import pygame as pg

from . import BaseScene, game, assets


class MainMenuScene(BaseScene):
    def update(self):
        for ev in self.get_events():
            if ev.type == pg.MOUSEBUTTONDOWN:
                if assets.menu_quit.collidepoint(*ev.pos):
                    game.stop()
                elif assets.menu_play.collidepoint(*ev.pos):
                    self.manager.spawn_scene(PlayScene)

    def draw(self, surface: pg.Surface):
        surface.blit(assets.menu_background, (0, 0))


class PlayScene(BaseScene):
    def init(self, *args, **kwargs):
        pass

    def update(self):
        pass

    def draw(self, surface: pg.Surface):
        pass
