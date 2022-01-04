from __future__ import annotations

import random as rd
import pygame as pg

from . import BaseScene, game, assets
from . import window

from simple_ai.simulation import Simulation
from simple_ai.simulation import TileType
from simple_ai import configs


default_fps = window.max_fps


def clamp(n, smallest, largest): return max(smallest, min(n, largest))


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
    bot_steps: int
    bot_point_focused: tuple[int, int]
    bot_focusing_left_moves: int
    is_bot_turn: bool

    def init(self, *args, **kwargs):
        self.simulation = Simulation()
        self.simulation.init()
        self.killed_clients = 0
        self.max_killed_clients = configs.clients_number - configs.required_alive_clients
        self.bot_steps = 0
        self.is_bot_turn = True
        self.bot_point_focused = (0, 0)
        self.bot_focusing_left_moves = 0

    def _check_del(self, x: int, y: int):
        tile = self.simulation.world.get(x, y)
        if tile[0] == TileType.entity:
            self.killed_clients += 1
            print(self.killed_clients)
            self.simulation.world.set(x, y, (TileType.nothing, None))

    def _safe_check_del(self, x: int, y: int):
        if self.killed_clients < self.max_killed_clients:
            self._check_del(x, y)
        else:
            self.simulation.restart_world(configs.clients_number)
            self.killed_clients = 0

    def del_relative(self, x: int, y: int):
        self._safe_check_del(x + self.simulation.player_pos[0], y + self.simulation.player_pos[1])

    def remove_eaten_by_player(self):
        self.del_relative(0, 0)
        self.del_relative(-1, 0)
        self.del_relative(1, 0)
        self.del_relative(0, -1)
        self.del_relative(0, 1)
        self.del_relative(-1, -1)
        self.del_relative(-1, 1)
        self.del_relative(1, -1)
        self.del_relative(1, 1)

    def update(self):
        self.simulation.step()

        if self.is_bot_turn:
            window.max_fps = -1
            self.update_bot()
        else:
            self.update_player()
            window.max_fps = default_fps

    def find_point(self):
        best: set[tuple[int, int]] = set()
        best_dist = -1

        for x, y, _ in self.simulation.iterate():
            dist = x + y - (self.simulation.player_pos[0] + self.simulation.player_pos[1])
            if best_dist == -1 or best_dist == dist:
                best.add((x, y))
            elif best_dist < dist:
                best_dist = dist
                best = {(x, y)}

        try:
            if self.bot_focusing_left_moves > 0:
                self.bot_focusing_left_moves -= 1
                if self.simulation.world.get(*self.bot_point_focused)[0] != TileType.entity:
                    self.bot_focusing_left_moves = 0
                return self.bot_point_focused
            chosen = rd.choice(list(best))
            self.bot_point_focused = chosen
            self.bot_focusing_left_moves = configs.bot_focused_by
        except IndexError:
            # no element
            self.simulation.restart_world(configs.clients_number)
            chosen = self.find_point()  # recursion error? Open simple_ai/configs.py. Is clients_number is bigger than 0
        return chosen

    @staticmethod
    def get_axis(x: int, y: int):
        return clamp(x, -1, 1), clamp(y, -1, 1)

    def bot_movement(self):
        ret = self.find_point()
        return self.get_axis(ret[0] - self.simulation.player_pos[0], ret[1] - self.simulation.player_pos[1])

    def update_bot(self):
        self.simulation.move_player(*self.bot_movement())
        self.remove_eaten_by_player()

    def update_player(self):
        pressed = pg.key.get_pressed()

        if pressed[pg.K_LEFT]:
            self.simulation.move_player(-1, 0)

        if pressed[pg.K_UP]:
            self.simulation.move_player(0, -1)

        if pressed[pg.K_RIGHT]:
            self.simulation.move_player(1, 0)

        if pressed[pg.K_DOWN]:
            self.simulation.move_player(0, 1)

        self.remove_eaten_by_player()

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
