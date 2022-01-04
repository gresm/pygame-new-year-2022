from __future__ import annotations

import pygame as pg

from . import BaseScene, game, assets

from simple_ai.simulation import Simulation
from simple_ai.simulation import TileType
from simple_ai import configs


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
    max_killed_clients: int

    def init(self, *args, **kwargs):
        self.simulation = Simulation()
        self.simulation.init()
        self.killed_clients = 0
        self.max_killed_clients = configs.clients_number - configs.required_alive_clients

    def update(self):
        # for ev in self.get_events():
        #     if ev.type == pg.KEYDOWN:
        #         if ev.key == pg.K_SPACE:
        #             for x, y, _ in self.simulation.iterate():
        #                 val = self.simulation.world.mutate(x, y)
        #                 if val is not None:
        #                     self.simulation.world.set((TileType.entity, val))
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

        def check_del(x: int, y: int):
            tile = self.simulation.world.get(x, y)
            if tile[0] == TileType.entity:
                self.killed_clients += 1
                print(self.killed_clients)
                self.simulation.world.set(x, y, (TileType.nothing, None))

        def safe_check_del(x: int, y: int):
            if self.killed_clients < self.max_killed_clients:
                check_del(x, y)
            else:
                self.simulation.restart_world(configs.clients_number)
                self.killed_clients = 0

        def safe_check_relative(x: int, y: int):
            safe_check_del(x + self.simulation.player_pos[0], y + self.simulation.player_pos[1])

        safe_check_relative(0, 0)
        safe_check_relative(-1, 0)
        safe_check_relative(1, 0)
        safe_check_relative(0, -1)
        safe_check_relative(0, 1)
        safe_check_relative(-1, -1)
        safe_check_relative(-1, 1)
        safe_check_relative(1, -1)
        safe_check_relative(1, 1)

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
