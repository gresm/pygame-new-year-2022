from __future__ import annotations

from .world import World, TileType
from . import configs as cf
from .network import Network, Neuron

import random as rd


class Simulation:
    def __init__(self):
        self.world = World()
        self.player_pos = (self.world.board.shape[0]//2,  self.world.board.shape[1]//2)

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

    def init(self):
        for _ in range(cf.clients_number):
            self.world.spawn()

    def exec(self, x, y, out: set[Neuron]):
        dx = 0
        dy = 0
        for el in out:
            if el.neuron_strength > 0.25:
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
        for x in range(self.world.board.shape[0]):
            for y in range(self.world.board.shape[1]):
                if self.world.board[x][y][0] == tile_type:
                    yield x, y, self.world.get(x, y)[1]

    def step(self):
        for x, y, data in self.iterate():
            self.run(x, y)

    def move_player(self, dx, dy):
        nx = self.player_pos[0] + dx
        ny = self.player_pos[1] + dy

        if self.world.inside(nx, ny):
            self.player_pos = (nx, ny)

    def restart_world(self, required_clients: int):
        clients = list(self.iterate())
        self.world = World()
        self.player_pos = (self.world.board.shape[0] // 2, self.world.board.shape[1] // 2)

        for _, _, cl in clients:
            self.world.respawn_random_where((TileType.entity, self.world.check_raw_mutate(cl)))

        try:
            for _ in range(required_clients - len(clients)):
                client = rd.choice(clients)
                self.world.respawn_random_where((TileType.entity, self.world.check_raw_mutate(client[2])))
        except IndexError:
            # somehow there are no clients in the world
            self.init()
