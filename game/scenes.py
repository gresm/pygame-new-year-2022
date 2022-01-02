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
    killed_clients: int

    def init(self, *args, **kwargs):
        self.simulation = Simulation()
        self.killed_clients = 0

    def update(self):
        pressed = pg.key.get_pressed()

        if pressed[pg.K_LEFT]:
            self.simulation.move_player(-1, 0)

        if pressed[pg.K_UP]:
            self.simulation.move_player(0, -1)

        if pressed[pg.K_RIGHT]:
            self.simulation.move_player(1, 0)

        if pressed[pg.K_DOWN]:
            self.simulation.move_player(0, 1)

        self.simulation.step()

    def draw(self, surface: pg.Surface):
        scale = 10
        offset = 150
        for x, y, info in self.simulation.iterate():
            px = x * scale + offset
            py = y * scale + offset
            surface.blit(assets.game_neuron_rect, (px, py))

        surface.blit(
            assets.game_player_rect,
            (
                self.simulation.player_pos[0] * scale + offset,
                self.simulation.player_pos[1] * scale + offset
            )
        )
