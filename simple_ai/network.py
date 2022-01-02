from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from functools import lru_cache

from . import operations
from .configs import ai_max_iterations


class NeuronType(Enum):
    input_neuron = 0
    hidden_neuron = 1
    output_neuron = 2


@dataclass(unsafe_hash=True)
class Neuron:
    neuron_type: NeuronType
    neuron_id: int
    neuron_strength: float

    def serialize(self, pretty: bool = True):
        str_id = hex(self.neuron_id)
        if len(str_id) == 3:
            str_id = str_id[0:2] + "0" + str_id[2]
        str_id = str_id[1:]
        str_strength = hex(int(self.neuron_strength * 255) % 256)
        if len(str_strength) == 3:
            str_strength = str_strength[0:2] + "0" + str_strength[2]
        str_strength = str_strength[1:]
        if pretty:
            return str(self.neuron_type.value) + str_id + str_strength
        return str(self.neuron_type.value) + str_id[1:] + str_strength[1:]

    @classmethod
    def deserialize(cls, text: str, pretty: bool = True):
        neuron_type = NeuronType(int(text[0]))
        if pretty:
            neuron_id = int(text[2:4], 16)
            neuron_strength = int(text[5:], 16) / 255
        else:
            neuron_id = int(text[1:3], 16)
            neuron_strength = int(text[3:], 16) / 255
        return cls(neuron_type, neuron_id, neuron_strength)


@dataclass(unsafe_hash=True)
class NeuralConnection:
    first: Neuron
    second: Neuron
    strength: float

    def serialize(self, pretty: bool = True):
        strength = hex(int(self.strength * 255) % 256)[2:]
        if len(strength) == 1:
            strength = "0" + strength
        first = self.first.serialize(pretty)
        second = self.second.serialize(pretty)
        if pretty:
            return f"{strength}+{first}+{second}"
        return strength + first + second

    @classmethod
    def deserialize(cls, text: str, pretty: bool = True):
        strength = int(text[:2], 16) / 255

        if pretty:
            first = Neuron.deserialize(text[3:10])
            second = Neuron.deserialize(text[11:])
        else:
            first = Neuron.deserialize(text[2:7], False)
            second = Neuron.deserialize(text[7:], False)

        return cls(first, second, strength)


@dataclass
class Network:
    input_neurons: set[Neuron]
    hidden_neurons: set[Neuron]
    output_neurons: set[Neuron]

    neuron_connections: set[NeuralConnection]

    def __hash__(self):
        return hash(id(self))

    def _add_neuron(self, neuron: Neuron):
        if neuron.neuron_type == NeuronType.input_neuron:
            self.input_neurons.add(neuron)
        elif neuron.neuron_type == NeuronType.hidden_neuron:
            self.hidden_neurons.add(neuron)
        elif neuron.neuron_type == NeuronType.output_neuron:
            self.output_neurons.add(neuron)
        else:
            raise ValueError(f"{neuron.neuron_type} is not an understandable neuron type")

    def _exec_neuron(self, neuron: Neuron, iteration: int):
        if iteration == 0:
            return

        for conn in self._get_neuron_connections(neuron):
            sent = operations.neuron_calculation(
                operations.sending_data(neuron.neuron_strength, conn.strength),
                conn.second.neuron_strength
            )

            conn.second.neuron_strength = sent
            self._exec_neuron(conn.second, iteration - 1)

    @lru_cache()
    def _get_neuron_connections(self, neuron: Neuron):
        connections: set[NeuralConnection] = set()
        for conn in self.neuron_connections:
            if conn.first is neuron:
                connections.add(conn)
        return connections

    def add_raw_connection(self, connection: NeuralConnection):
        self._add_neuron(connection.first)
        self._add_neuron(connection.second)
        self.neuron_connections.add(connection)

    def add_connection(self, connection_string: str, pretty: bool = True):
        self.add_raw_connection(NeuralConnection.deserialize(connection_string, pretty))

    def run_network(self, inputs: dict[int, float]) -> set[Neuron]:
        ser = self.serialize(True)
        for el in self.input_neurons:
            if el.neuron_id in inputs:
                el.neuron_strength = inputs[el.neuron_id]
                self._exec_neuron(el, ai_max_iterations)

        ret = self.output_neurons.copy()
        self.deserialize_ip(ser, True)
        return ret

    def serialize(self, pretty: bool = True):
        return tuple(el.serialize(pretty) for el in self.neuron_connections)

    def deserialize_ip(self, text: tuple[str], pretty: bool = True):
        self.input_neurons = set()
        self.hidden_neurons = set()
        self.output_neurons = set()
        self.neuron_connections = set()

        for el in text:
            self.add_connection(el, pretty)

    @classmethod
    def get(cls):
        return cls(set(), set(), set(), set())

    @classmethod
    def deserialize(cls, text: tuple[str], pretty: bool = True):
        ret = cls.get()
        ret.deserialize_ip(text, pretty)
        return ret


__all__ = [
    "NeuronType",
    "Neuron",
    "NeuralConnection",
    "Network"
]
