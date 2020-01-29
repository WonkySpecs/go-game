import socket

from raylib.static import *

from game import Game, Colour
from interface import GUI, Interface

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600


def run(net_conn: socket.socket, player_colour):
    net_conn.setblocking(False)
    grid_dims = grid_width, grid_height = 19, 19
    game = Game(grid_width, grid_height, player_colour)
    gui = GUI(SCREEN_WIDTH, SCREEN_HEIGHT, grid_dims)
    interface = Interface(gui, net_conn)

    title = f"Go | You play {'white' if player_colour == Colour.WHITE else 'black'}"
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, title.encode('ascii'))
    SetTargetFPS(60)

    while not WindowShouldClose():
        interface.handle_inputs(game)
        gui.draw(game)
    net_conn.close()
    CloseWindow()

