from enum import Enum, auto
import socket

from main import run
from game import Colour


class Mode(Enum):
    HOST = auto()
    JOIN = auto()


PORT = 8642

print("Welcome")
print("-------")
print("Would you like to (H)ost a new game, or (J)oin an existing one?")

while True:
    mode_in = input()
    if mode_in in ["H", "h", "J", "j"]:
        mode = Mode.HOST if mode_in in ["H", "h"] else Mode.JOIN
        break
    print("Invalid, enter 'H' to host a game, or 'J' to join one someone else is hosting")

sock = socket.socket()
connection = sock

if mode == Mode.JOIN:
    print("Enter the ip to connect to")
    while True:
        addr_in = input()
        try:
            sock.connect((addr_in, PORT))
            break
        except Exception as e:
            print(f"Failed with exception {e}\nTry again")

if mode == Mode.HOST:
    sock.bind(("localhost", PORT))
    sock.listen()
    connection, addr = sock.accept()
    print(f"{addr} connected, starting game.")

run(connection, Colour.BLACK if mode == Mode.HOST else Colour.WHITE)
