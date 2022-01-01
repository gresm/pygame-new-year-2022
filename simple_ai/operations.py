import math as mt


def connection_strength(input_value: float, neuron_strength: float) -> float:
    """
    Calculates sent value by neuron connection.
    :param input_value: float between 0 and 1
    :param neuron_strength: float between 0 and 1
    :return: float between 0 and 1
    """
    return mt.tanh(input_value * neuron_strength * 2)


def neuron_calculation(input_value: float, neuron_weight: float) -> float:
    """
    Calculates output value of neuron.
    :param input_value: float between 0 and 1
    :param neuron_weight: float between 0 and 1
    :return: float between 0 and 1
    """
    return mt.tanh(input_value + neuron_weight)


__all__ = [
    "connection_strength",
    "neuron_calculation"
]
