import socket
import json

class GameConnection:
    def __init__(self, port=5555):
        self.port = port
        self.socket = None
        self.connection = None
        
    def host_game(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', self.port))
        self.socket.listen(1)
        print("Waiting for opponent to join...")
        self.connection, addr = self.socket.accept()
        print("Opponent connected from:", addr)
        return True

    def join_game(self, host):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, self.port))
            self.connection = self.socket
            print("Connected to host!")
            return True
        except:
            print("Could not connect to host")
            return False

    def send_move(self, space, steps, rolls=None):
        """
        Send the move and dice rolls as a JSON message to the opponent.
        """
        msg = json.dumps({
            'space': space, 
            'steps': steps,
            'rolls': rolls  # Include dice rolls in the message
        })
        self.connection.sendall(msg.encode())  # Ensure complete message is sent


    def receive_move(self):
        """
        Receive the move from the opponent as a JSON message.
        """
        try:
            data = self.connection.recv(1024).decode()  # Receive data from socket
            if data:
                return json.loads(data)  # Convert JSON message to dictionary
        except Exception as e:
            print(f"Error receiving move: {e}")
            return None


    def close(self):
        if self.connection:
            self.connection.close()
        if self.socket:
            self.socket.close()
