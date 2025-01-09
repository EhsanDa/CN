import socket
import random
import json
from pymongo import MongoClient

def parse_message(message):
    return json.loads(message)

class GameServer:
    def __init__(self, host="127.0.0.1", port=65432,
                 db_uri="mongodb://user:password@localhost:27017/game_db", 
                 db_name="game_db"):
        self.server_address = (host, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client = MongoClient(db_uri)
        self.db = self.client[db_name]
        self.players_collection = self.db['players']
        self.requests_collection = self.db['requests']  # New collection for requests


    def start(self):
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(5)
        
        print(f"Server listening on {self.server_address}")
        
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection from {client_address}")
            self.handle_client(client_socket)

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode("utf-8").strip()
                if not message:
                    break
                
                print(f"Received: {message}")
                payload = json.loads(parse_message(message)['payload'])
                response = self.process_message(payload)
                client_socket.sendall(response.encode("utf-8"))
        except ConnectionError:
            print("Client disconnected")
        finally:
            client_socket.close()

    def process_message(self, payload):
        command = payload.get('command')

        if command == "start game":
            new_player = {
                'ip': payload.get('ip'),
                'name': payload.get('name', 'Anonymous'),
            }
            self.players_collection.insert_one(new_player)  # Store new player in MongoDB
            return json.dumps({'result': "Player added to ready_players"})

        elif command == "get ready players":
            ready_players = list(self.players_collection.find({}, {'_id': 0}))  # Retrieve players from MongoDB
            return json.dumps({'result': ready_players})

        elif command == "roll dice":
            dice1_roll = random.randint(1, 6)
            dice2_roll = random.randint(1, 6)
            result = [dice1_roll, dice2_roll]  # Create the list directly with both rolls.
            return json.dumps({'result': result})
        
        elif command == "request player":
            requester_name = payload.get('name')
            target_name = payload.get('target_name')
            
            print(payload)

            # Store the request in the requests collection
            request_data = {
                'requester_name': requester_name,
                'target_name': target_name,
                'host_socket': payload.get('socket'),
                'ip': payload.get('ip'),
                'status': 'pending'
            }
            self.requests_collection.insert_one(request_data)  # New line to save the request

            return json.dumps({'result': f"Connection request sent to {target_name}"})
        
        elif command == "get requests":
            user_name = payload.get('name')
            # Find requests where the target is the user
            user_requests = list(self.requests_collection.find({'target_name': user_name}, {'_id': 0}))
            return json.dumps({'result': user_requests})
        
        else:
            return json.dumps({'result': "Unknown command"})

if __name__ == "__main__":
    server = GameServer()
    server.start()