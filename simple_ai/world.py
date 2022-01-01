import numpy as np

from .configs import map_size


class Board:
    def __init__(self):
        self.board = np.full(map_size, (0, None), dtype=[("tile_type", int), ("info", object)])
