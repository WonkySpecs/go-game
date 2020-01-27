from raylib.static import *

from game import Game
from drawing import GUI

SCREEN_WIDTH, SCREEN_HEIGHT = 1440, 900


def run():
    grid_dims = grid_width, grid_height = 19, 19
    game = Game(grid_width, grid_height)
    gui = GUI(SCREEN_WIDTH, SCREEN_HEIGHT, grid_dims)

    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, b"Go")
    SetWindowTitle(b"This can be changed (to show status? does show when alt-tabbing)")
    SetTargetFPS(60)
    print("Starting")

    while not WindowShouldClose():
        gui.handle_inputs(game)
        gui.draw(game)
    CloseWindow()
