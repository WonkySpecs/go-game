from typing import Tuple, List

from raylib.static import *
from game import Colour

from game import Game

# Assumption being made that grid is square in lots of places


class GUI:
    def __init__(self, screen_width: int, screen_height: int, grid_dims: Tuple[int, int], conn):
        self.grid_dims = grid_dims
        smaller_screen_dim = min(screen_width, screen_height)
        self.edge_length: float = smaller_screen_dim * 9 / 10
        self.grid_origin: Tuple[float, float] =\
            ((screen_width - self.edge_length) / 2, (screen_height - self.edge_length) / 2)

        grid_spacing_x = self.edge_length / (grid_dims[0] - 1)
        grid_spacing_y = self.edge_length / (grid_dims[1] - 1)
        self.grid_columns: List[List[Tuple[float, float]]] = [[
            (self.grid_origin[0] + int(x * grid_spacing_x), self.grid_origin[1]),
            (self.grid_origin[0] + int(x * grid_spacing_x), self.grid_origin[1] + self.edge_length)]
            for x in range(grid_dims[0])]
        self.grid_rows = [[
            (self.grid_origin[0], self.grid_origin[1] + int(y * grid_spacing_y)),
            (self.grid_origin[0] + self.edge_length, self.grid_origin[1] + int(y * grid_spacing_y))]
            for y in range(grid_dims[1])]
        # No the GUI should not have a reference to the socket
        # Yes I want something fast before I go to bed
        self.conn = conn

    def handle_inputs(self, game: Game):
        if game.my_turn and IsMouseButtonReleased(MOUSE_LEFT_BUTTON):
            x, y = self._world_to_grid(GetMouseX(), GetMouseY())
            if x is None or y is None:
                return

            if game.is_valid_move(x, y):
                game.play(x, y)
                self.conn.send(f"{x},{y}".encode('ascii'))

    def draw(self, game: Game):
        BeginDrawing()
        ClearBackground(BEIGE)

        for start, end in self.grid_columns:
            DrawLineV(start, end, BLACK)
        for start, end in self.grid_rows:
            DrawLineV(start, end, BLACK)

        for x in range(self.grid_dims[0]):
            for y in range(self.grid_dims[1]):
                stone = game.grid[x][y]
                if stone is None:
                    continue
                colour = BLACK if stone == Colour.BLACK else WHITE
                DrawCircleV(self._grid_to_world(x, y), 15, colour)
        EndDrawing()

    def _world_to_grid(self, wx: float, wy: float):
        offset = wx - self.grid_origin[0], wy - self.grid_origin[1]
        x = (self.grid_dims[0] - 1) * offset[0] / self.edge_length
        y = (self.grid_dims[1] - 1) * offset[1] / self.edge_length

        def too_far(fractional):
            return abs(fractional - round(fractional)) > 0.2

        if too_far(x) or too_far(y):
            return None, None

        return round(x), round(y)

    def _grid_to_world(self, x: int, y: int):
        return [self.grid_origin[0] + self.edge_length * (x / (self.grid_dims[0] - 1)),
                self.grid_origin[1] + self.edge_length * (y / (self.grid_dims[1] - 1))]
