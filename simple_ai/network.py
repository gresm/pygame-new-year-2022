from enum import Enum
from dataclasses import dataclass


class NeuronType(Enum):
    input_neuron = 0
    hidden_neuron = 1
    output_neuron = 2


@dataclass
class Neuron:
    __slots__ = ("neuron_type", "neuron_id", "neuron_strength")

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


@dataclass
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
