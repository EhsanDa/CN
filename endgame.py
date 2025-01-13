import json
import threading
from utils.handshake import *
from utils.keyReader import *
from utils.sendmessage import *

def check_end_game(b):
    message = "check end game"
    board = b.to_dict()
    x = {
        "command": message,
        "board": board
    }
    print(x)
    y = json.dumps(x)
    response = send_message(y)
    print(response)
    data = json.loads(response)
    # Access the rolls
    game_over = data['game_over']
    winner = data['winner']
    message = data['message']
    return game_over, winner, message
