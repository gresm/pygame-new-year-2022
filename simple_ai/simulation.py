from __future__ import annotations

from .world import World, TileType
from . import configs as cf
from .network import Network, Neuron

import random as rd


class Simulation:
    def __init__(self):
        self.world = World()
        self.player_pos = (0, 0)

        for _ in range(cf.clients_number):
            self.world.spawn()

    def get_inputs(self, x: int, y: int) -> list[float]:
        ret: list[float] = [0 for _ in range(10)]

        shape = self.world.board.shape
        x_prop = x / shape[0]
        y_prop = y / shape[1]
        ret[0] = x_prop
        ret[1] = y_prop

        plx_prop = self.player_pos[0] / shape[0]
        ply_prop = self.player_pos[1] / shape[1]
        ret[2] = plx_prop
        ret[3] = ply_prop

        left_ness = self.world.get(x - 1, y)[0] == TileType.nothing
        right_ness = self.world.get(x + 1, y)[0] == TileType.nothing
        up_ness = self.world.get(x, y - 1)[0] == TileType.nothing
        down_ness = self.world.get(x, y + 1)[0] == TileType.nothing
        ret[4] = left_ness
        ret[5] = right_ness
        ret[6] = up_ness
        ret[7] = down_ness

        random_ness = rd.random()
        ret[8] = random_ness

        return ret

    def exec(self, x, y, out: set[Neuron]):
        dx = 0
        dy = 0
        for el in out:
            if el.neuron_strength > 0.5:
                if el.neuron_id == 0:
                    dx -= 1
                if el.neuron_id == 1:
                    dy -= 1
                if el.neuron_id == 2:
                    dx += 1
                if el.neuron_id == 3:
                    dy += 1

        self.world.move(x, y, dx, dy)

    def run(self, x, y):
        net = Network.deserialize(self.world.board[x][y][1])
        feed = self.get_inputs(x, y)
        inp = {i: feed[i] for i in range(10)}
        self.exec(x, y, net.run_network(inp))

    def iterate(self, tile_type: int = TileType.entity):
        for x in self.world.board:
            for y in self.world.board[x]:
                if self.world.board[x][y][0] == tile_type:
                    yield x, y, self.world.board[x][y][1]

    def step(self):
        for x, y, data in self.iterate():
            self.run(x, y)
