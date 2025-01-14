import json
import threading
from utils.handshake import *
from utils.keyReader import *
from utils.sendmessage import *
from roll_dice import *

from backgammon import *

from chat import *

# Perform handshake first
handshake()

def start_client():
    name = None
    ip = None

    while True:
        # Allow input for name and IP only once at the start of the game
        if not name or not ip:
            name = input("Enter your Name: ").strip()
            ip = input("Enter your IP: ").strip()

        # Display available commands
        message = input("Enter your message (start game, request player <name>, get requests, I'm ready to game, roll dice, get ready players, accept <name>, or exit to leave): ").lower()
    
        if message == "exit":
            print("Exiting the game.")
            break

        # Handle 'start game' command
        if message == "start game":
            x = {
                "name": name,
                "ip": ip,
                "command": message
            }
            y = json.dumps(x)
            send_message(y)

        # Handle 'request player' command
        elif message.startswith("request player"):
            target_name = message.split(maxsplit=2)[2]  # Get the name from the command
            host_socket = input("Enter your Port Number: ").strip()
            x = {
                "ip": ip,
                "command": "request player",
                "target_name": target_name,
                "name": name,
                "socket": host_socket
            }
            y = json.dumps(x)
            send_message(y)

            # Start the chat in a new thread
            chat_thread = threading.Thread(target=start_chat, args=(name, 'host', ip, 9099))
            chat_thread.start()

            # Proceed with the game
            startgame(ip, int(host_socket), 'h')

        # Handle 'get ready players' command
        elif message == "get ready players":
            x = {
                "command": message
            }
            y = json.dumps(x)
            send_message(y)

        # Handle 'I'm ready to game' command
        elif message == "i'm ready to game":
            x = {
                "command": message,
                "name": name,
                "ip": ip
            }
            y = json.dumps(x)
            send_message(y)

        elif message == "get requests":
            x = {
                "command": "get requests",
                "name": name
            }
            y = json.dumps(x)
            response = send_message(y)
            
            data = json.loads(response)
            other_player_info = data['result'][0]

        # Handle 'accept connection' command
        elif message.startswith("accept"):
            # Start the chat in a new thread
            chat_thread = threading.Thread(target=start_chat, args=(name, 'join', other_player_info['ip'], 9099))
            chat_thread.start()

            # Proceed with the game
            startgame(other_player_info['ip'], int(other_player_info['host_socket']), 'j')

        # Handle 'roll dice' command
        elif message == "roll dice":
            roll_dices()

        else:
            print("Unknown command! Please try again.")

if __name__ == "__main__":
    start_client()
