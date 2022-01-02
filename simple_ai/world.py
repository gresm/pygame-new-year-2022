from __future__ import annotations

import random as rd
import numpy as np

from . import configs as cf
from .network import *


class TileType:
    nothing = 0
    entity = 1
    wall = 2


class World:
    def __init__(self):
        self.board = np.full(cf.map_size, (TileType.nothing, None), dtype=object)

    def _move(self, x1, y1, x2, y2):
        x2 %= self.board.shape[0]
        y2 %= self.board.shape[1]

        if self.get(x1, y1)[0] == TileType.wall:
            return False

        if self.get(x2, y2)[0] != TileType.nothing:
            return False

        self.set(x2, y2, self.get(x1, y1))
        self.set(x1, y1, (0, None))
        return True

    def move(self, x: int, y: int, dx: int, dy: int):
        return self._move(x, y, x+dx, y+dy)

    def spawn(self):
        x = rd.randint(0, self.board.shape[0] - 1)
        y = rd.randint(0, self.board.shape[1] - 1)
        conn = rd.randint(0, cf.max_connections)
        input_neurons = rd.randint(0, cf.max_input_neurons)
        output_neurons = rd.randint(0, cf.max_output_neurons)
        hidden_neurons = rd.randint(0, cf.max_hidden_neurons)
        real_neurons = rd.randint(conn//2, conn+conn//2)

        network = Network.get()
        neurons = set()

        def spawn_neuron(neuron_id: int):
            if 0 <= neuron_id < input_neurons:
                neuron_type = 0
            elif input_neurons <= neuron_id < input_neurons + output_neurons:
                neuron_type = 2
                neuron_id -= input_neurons
            else:
                neuron_type = 1
                neuron_id -= input_neurons + output_neurons
            return Neuron(NeuronType(neuron_type), neuron_id, 0)

        def correct_order(f: Neuron, s: Neuron):
            if f.neuron_type == NeuronType.input_neuron:
                return f, s
            if f.neuron_type == NeuronType.output_neuron:
                return s, f
            if s.neuron_type == NeuronType.input_neuron:
                return s, f
            if s.neuron_type == NeuronType.output_neuron:
                return f, s
            return f, s

        for _ in range(real_neurons):
            nid = rd.randint(0, input_neurons + output_neurons + hidden_neurons)
            neurons.add(spawn_neuron(nid))

        try:
            for _ in range(conn):
                first = rd.choice(list(neurons))
                neurons.remove(first)
                second = rd.choice(list(neurons))
                neurons.add(first)
                cor = correct_order(first, second)
                connection = NeuralConnection(cor[0], cor[1], rd.random())
                network.add_raw_connection(connection)
        except IndexError:
            pass

        serialized = network.serialize()
        self.board[x][y] = (TileType.entity, serialized)

    def mutate(self, x: int, y: int) -> tuple[str, ...] | None:
        val = self.get(x, y)

        if val[0] != TileType.entity:
            return val[1]
        ret = val[1]

        for _ in range(rd.randint(1, cf.mutation_max_iterations)):
            try:
                ret = self._mutate(ret)
            except IndexError:
                pass
        return ret

    @staticmethod
    def _mutate(net):
        # noinspection PyTypeChecker
        net = Network.deserialize(net)
        action = rd.randint(0, 3)

        if action == 0:
            # connection strength
            conn = rd.choice(list(net.neuron_connections))
            conn.strength = rd.random()
        elif action == 1:
            # connection between existing
            ft = rd.randint(0, 1)
            st = rd.randint(0, 1)

            if not ft:
                first = rd.choice(list(net.input_neurons))
                if st:
                    second = rd.choice(list(net.output_neurons))
                else:
                    second = rd.choice(list(net.hidden_neurons))
            else:
                first = rd.choice(list(net.hidden_neurons))
                if st:
                    second = rd.choice(list(net.output_neurons))
                else:
                    second = rd.choice(list(net.hidden_neurons))

            net.add_raw_connection(NeuralConnection(first, second, rd.random()))
        elif action == 2:
            # connection between new and existing
            ex = rd.choice(list(net.neuron_connections)).first

            input_neurons = rd.randint(0, cf.max_input_neurons)
            output_neurons = rd.randint(0, cf.max_output_neurons)
            hidden_neurons = rd.randint(0, cf.max_hidden_neurons)

            def spawn_neuron(op: int):
                if op == 0:
                    return Neuron(NeuronType(op), input_neurons, 0)
                elif op == 1:
                    return Neuron(NeuronType(op), hidden_neurons, 0)
                return Neuron(NeuronType(op), output_neurons, 0)

            new = spawn_neuron(rd.randint(0, 2))
            conn = NeuralConnection(ex, new, rd.random())
            net.add_raw_connection(conn)
        else:
            # removing of existing connection
            net.neuron_connections.remove(rd.choice(list(net.neuron_connections)))

        return net.serialize()

    def get(self, x: int, y: int):
        if self.inside(x, y):
            return self.board[x][y]
        return TileType.wall, None

    def set(self, x: int, y: int, val):
        if self.inside(x, y):
            self.board[x][y] = val

    def inside(self, x: int, y: int):
        return 0 <= x < self.board.shape[0] and 0 <= y < self.board.shape[1]

    def check_mutate(self, x: int, y: int):
        if rd.randint(0, cf.randomness_scale) <= cf.mutation_chance:
            return self.mutate(x, y)
        return self.get(x, y)[1]


__all__ = [
    "TileType",
    "World"
]
