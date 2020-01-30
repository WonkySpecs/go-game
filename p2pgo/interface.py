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
        handler = self._handle_gui_interactions if game.my_turn else self._handle_network_interaction
        handler(game)

    def _handle_gui_interactions(self, game):
        click = self.gui.get_grid_click()
        if click:
            x, y = click
            valid, msg = game.is_valid_move(x, y)
            if valid:
                game.play(x, y)
                self.conn.send(f"{x},{y}".encode('ascii'))
                self.gui.ghost = None
            else:
                self.gui.error_message = msg

        button_pressed = self.gui.get_button_press()
        if button_pressed == "pass":
            game.pass_turn()
            self.conn.send(b"pass")

        self.gui.set_ghost(game.player_colour)

    def _handle_network_interaction(self, game):
        try:
            msg = self.conn.recv(1024)
            if msg == b"pass":
                game.pass_turn()
            else:
                x, y, = [int(coord) for coord in msg.decode('ascii').split(",")]
                game.play(x, y)
        except BlockingIOError:
            # Thrown if nothing has been received
            pass


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
        self.ghost: Optional[Tuple[Colour, Tuple[int, int]]] = None
        self.stone_size = grid_spacing_x / 2.4
        self.error_message: Optional[str] = None
        self.error_timer: int = 170
        self.buttons = {
            ("pass", b"Pass Turn"): (5,
                                     round(screen_height / 2),
                                     105,
                                     25),
        }

    def get_grid_click(self) -> Optional[Tuple[int, int]]:
        if IsMouseButtonReleased(MOUSE_LEFT_BUTTON):
            return self._world_to_grid(GetMouseX(), GetMouseY())

    def get_button_press(self):
        if IsMouseButtonReleased(MOUSE_LEFT_BUTTON):
            for (name, _), area in self.buttons.items():
                if GUI._in_rectangle(GetMouseX(), GetMouseY(), area):
                    return name

    @staticmethod
    def _in_rectangle(x: int, y: int, rect: Tuple[int, int, int, int]):
        return rect[0] <= x <= rect[0] + rect[2] and rect[1] <= y <= rect[1] + rect[3]

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
                DrawCircleV(self._grid_to_world(x, y), self.stone_size, colour)

        for (_, text), area in self.buttons.items():
            col = DARKGRAY if GUI._in_rectangle(GetMouseX(), GetMouseY(), area) else GRAY
            DrawRectangle(area[0], area[1], area[2], area[3], col)
            DrawText(text, area[0] + 5, area[1] + 2, 18, BLACK)

        if self.ghost:
            colour, (x, y) = self.ghost
            DrawCircleV(self._grid_to_world(x, y),
                        self.stone_size / 1.8,
                        BLACK if colour == Colour.BLACK else WHITE)

        if self.error_message:
            msg = self.error_message.encode("ascii")
            font_size = 25
            msg_width = MeasureText(msg, font_size)
            msg_x = round(GetScreenWidth() / 2 - msg_width / 2)
            msg_y = GetScreenHeight() - 40

            if self.error_timer % 30 < 25:
                DrawText(msg, msg_x, msg_y, font_size, RED)

            self.error_timer -= 1
            if self.error_timer < 0:
                self.error_message = None
                self.error_timer = 170

        EndDrawing()

    def _world_to_grid(self, wx: float, wy: float) -> Optional[Tuple[int, int]]:
        offset = wx - self.grid_origin[0], wy - self.grid_origin[1]
        x = (self.grid_dims[0] - 1) * offset[0] / self.edge_length
        y = (self.grid_dims[1] - 1) * offset[1] / self.edge_length

        def too_far(fractional):
            return abs(fractional - round(fractional)) > 0.3

        if round(x) < 0 or round(y) < 0 or too_far(x) or too_far(y):
            return None

        return round(x), round(y)

    def _grid_to_world(self, x: int, y: int) -> Tuple[float, float]:
        return (self.grid_origin[0] + self.edge_length * (x / (self.grid_dims[0] - 1)),
                self.grid_origin[1] + self.edge_length * (y / (self.grid_dims[1] - 1)))

    def set_ghost(self, colour):
        mouse_grid_pos = self._world_to_grid(GetMouseX(), GetMouseY())
        if mouse_grid_pos:
            self.ghost = (colour, (mouse_grid_pos[0], mouse_grid_pos[1]))
        else:
            self.ghost = None
