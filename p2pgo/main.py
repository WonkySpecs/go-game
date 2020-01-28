import socket

from raylib.static import *

from game import Game
from drawing import GUI

SCREEN_WIDTH, SCREEN_HEIGHT = 1440, 900


def run(net_conn: socket.socket, player_colour):
    net_conn.setblocking(False)
    grid_dims = grid_width, grid_height = 19, 19
    game = Game(grid_width, grid_height, player_colour)
    # No the GUI should not have a reference to the socket
    # Yes I want something fast before I go to bed
    gui = GUI(SCREEN_WIDTH, SCREEN_HEIGHT, grid_dims, net_conn)

    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, b"Go")
    SetWindowTitle(b"This can be changed (to show status? does show when alt-tabbing)")
    SetTargetFPS(60)

    while not WindowShouldClose():
        gui.handle_inputs(game)
        handle_network_input(net_conn, game)
        gui.draw(game)
    CloseWindow()


def handle_network_input(net_conn, game):
    try:
        msg = net_conn.recv(1024)
        x, y, = [int(coord) for coord in msg.decode('ascii').split(",")]
        game.play(x, y)
    except BlockingIOError:
        return
