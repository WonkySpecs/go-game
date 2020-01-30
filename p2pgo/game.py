from enum import Enum, auto
from typing import List, Optional, Tuple, Iterable
from copy import deepcopy


# We keep up to this many previous board states to check for ko
MAX_HISTORY_ENTRIES = 20


class Colour(Enum):
    BLACK = auto()
    WHITE = auto()


class Game:
    def __init__(self, board_width, board_height, player_colour):
        self.grid: List[List[Optional[Colour]]] = self._empty_grid(board_width, board_height)
        self.current_player: Colour = Colour.BLACK
        self.player_colour: Colour = player_colour
        self._board_history: List[List[List[Optional[Colour]]]] = []

    def is_valid_move(self, x: int, y: int) -> Tuple[bool, Optional[str]]:
        if self.grid[x][y] is not None:
            return False, "There is already a stone there"

        invalid_checks = {
            "Suicidal moves not allowed": lambda: self._is_suicide(x, y),
            "Cannot repeat board state": lambda: self._repeated_board_state(),
        }

        self.grid[x][y] = self.current_player
        for msg, check in invalid_checks.items():
            if check():
                self.grid[x][y] = None
                return False, msg
        self.grid[x][y] = None

        return True, None

    def _is_suicide(self, x: int, y: int):
        if self._is_group_alive(self._get_group_at(x, y)):
            return False

        # If play captures any neighbouring group, it is not suicide
        for nx, ny in self._neighbours(x, y):
            if self.grid[nx][ny] == self.grid[x][y]:
                continue
            group = self._get_group_at(nx, ny)
            if not self._is_group_alive(group):
                return False
        return True

    def _repeated_board_state(self):
        # Reversed as more likely to be from a recent move
        for prev_grid in reversed(self._board_history):
            if self.grid == prev_grid:
                return True
        return False

    def play(self, x: int, y: int):
        self.grid[x][y] = self.current_player

        self._board_history.append(deepcopy(self.grid))
        if len(self._board_history) > MAX_HISTORY_ENTRIES:
            self._board_history = self._board_history[1:]

        if self.current_player == Colour.BLACK:
            self.current_player = Colour.WHITE
        else:
            self.current_player = Colour.BLACK
        self._capture_around(self.current_player, x, y)

    def _capture_around(self, colour_to_capture: Colour, x: int, y: int):
        for nx, ny in self._neighbours(x, y):
            if self.grid[nx][ny] == colour_to_capture:
                group = self._get_group_at(nx, ny)
                if not self._is_group_alive(group):
                    for (x, y) in group:
                        self.grid[x][y] = None

    def _get_group_at(self, x: int, y: int) -> Iterable[Tuple[int, int]]:
        to_visit = [(x, y)]
        group = []

        def should_visit(coord):
            return coord not in to_visit \
                and coord not in group \
                and self.grid[coord[0]][coord[1]] == self.grid[x][y]

        while to_visit:
            visiting = to_visit.pop()
            to_visit.extend([c for c in self._neighbours(visiting[0], visiting[1])
                             if should_visit(c)])
            group.append(visiting)
        return group

    def _is_group_alive(self, group: Iterable[Tuple[int, int]]):
        for x, y in group:
            for nx, ny in self._neighbours(x, y):
                if self.grid[nx][ny] is None:
                    return True
        return False

    def _neighbours(self, x: int, y: int):
        def in_grid(coord):
            return 0 <= coord[0] < len(self.grid) and 0 <= coord[1] < len(self.grid[0])

        return filter(in_grid, [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)])

    @property
    def my_turn(self):
        return self.current_player == self.player_colour

    @staticmethod
    def _empty_grid(width, height):
        return [[None for _ in range(height)] for _ in range(width)]
