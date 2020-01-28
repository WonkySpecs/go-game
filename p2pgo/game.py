from enum import Enum, auto
from typing import List, Optional


class Colour(Enum):
    BLACK = auto()
    WHITE = auto()


class Game:
    def __init__(self, board_width, board_height, player_colour):
        self.grid: List[List[Optional[Colour]]] = self._empty_grid(board_width, board_height)
        self.current_player: Colour = Colour.BLACK
        self.player_colour = player_colour

    def is_valid_move(self, x: int, y: int):
        # TODO: Check ko + suicide
        return self.grid[x][y] is None

    def play(self, x: int, y: int):
        self.grid[x][y] = self.current_player
        if self.current_player == Colour.BLACK:
            self.current_player = Colour.WHITE
        else:
            self.current_player = Colour.BLACK

    @property
    def my_turn(self):
        return self.current_player == self.player_colour

    @staticmethod
    def _empty_grid(width, height):
        return [[None for _ in range(height)] for _ in range(width)]
