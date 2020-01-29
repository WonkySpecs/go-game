from typing import Tuple, List, TYPE_CHECKING, Optional

from raylib.static import *
from game import Colour

from game import Game

if TYPE_CHECKING:
    import socket


class Interface:
    def __init__(self, gui: 'GUI', conn: 'socket.socket'):
        self.gui = gui
        self.conn = conn

    def handle_inputs(self, game):
        if game.current_player == game.player_colour:
            click = self.gui.grid_was_clicked()
            if click:
                x, y = click
                game.play(x, y)
                self.conn.send(f"{x},{y}".encode('ascii'))
        else:
            try:
                msg = self.conn.recv(1024)
                x, y, = [int(coord) for coord in msg.decode('ascii').split(",")]
                game.play(x, y)
            except BlockingIOError:
                # Thrown if nothing has been received
                return
        # Ghost


# Assumption being made that grid is square in lots of places
class GUI:
    def __init__(self, screen_width: int, screen_height: int, grid_dims: Tuple[int, int]):
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

    def grid_was_clicked(self) -> Optional[Tuple[int, int]]:
        if IsMouseButtonReleased(MOUSE_LEFT_BUTTON):
            return self._world_to_grid(GetMouseX(), GetMouseY())

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

    def _world_to_grid(self, wx: float, wy: float) -> Optional[Tuple[int, int]]:
        offset = wx - self.grid_origin[0], wy - self.grid_origin[1]
        x = (self.grid_dims[0] - 1) * offset[0] / self.edge_length
        y = (self.grid_dims[1] - 1) * offset[1] / self.edge_length

        def too_far(fractional):
            return abs(fractional - round(fractional)) > 0.3

        if too_far(x) or too_far(y):
            return None

        return round(x), round(y)

    def _grid_to_world(self, x: int, y: int) -> Tuple[float, float]:
        return (self.grid_origin[0] + self.edge_length * (x / (self.grid_dims[0] - 1)),
                self.grid_origin[1] + self.edge_length * (y / (self.grid_dims[1] - 1)))
