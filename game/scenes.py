from __future__ import annotations

import pygame as pg

from . import BaseScene, game, assets

from simple_ai.simulation import Simulation


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
    simulation: Simulation

    def init(self, *args, **kwargs):
        self.simulation = Simulation()

    def update(self):
        self.simulation.step()

    def draw(self, surface: pg.Surface):
        for x, y, info in self.simulation.iterate():
            px = x * 10 + 100
            py = y * 10 + 100
            pg.draw.rect(surface, (255, 255, 255), (px, py, 10, 10))
