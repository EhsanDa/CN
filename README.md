# Backgammon Game with Onion Routing Network

## Project Overview
An online multiplayer Backgammon game using onion routing for secure communication, featuring P2P gameplay with centralized server management for matchmaking and game state verification.

## Core Architecture

### Network Components
1. **Onion Routing Layer**
   - [node1.py](node1.py): First router (Port 5001)
   - [node2.py](node2.py): Second router (Port 7002)
   - [node3.py](node3.py): Final router (Port 8003)
   - [server/server.py](server/server.py): Game server (Port 65432)

### Game Components
- [backgammon.py](backgammon.py): Main game logic
- [board.py](board.py): Board state management
- [client.py](client.py): Client interface
- [chat.py](chat.py): P2P chat functionality

## Gameplay Flow

1. **Initial Connection**
```python
# Client starts with handshake
handshake()  # Establishes secure connections with routers
```

2. **Player Registration**
```python
# Player registers with server
{
    "command": "start game",
    "name": player_name,
    "ip": player_ip
}
```

3. **Game Request Flow**
```mermaid
sequenceDiagram
    Player1->>Server: request player <name>
    Server-->>Player2: store request
    Player2->>Server: get requests
    Player2->>Server: accept <name>
    Player1<->Player2: Establish P2P connection
```

4. **P2P Game Session**
- Players connect directly for game moves
- Server handles:
  - Dice rolls (`roll_dice()`)
  - End game verification (`check_end_game()`)

### Gameplay Components

#### Dice Rolling
```python
def roll_dices():
    message = {
        "command": "roll dice"
    }
    response = send_message(json.dumps(message))
    return json.loads(response)['result']
```

#### Move Validation ([board.py](board.py))
```python
def makeMove(self, space, side, steps):
    # Validates and executes moves
    # Handles:
    # - Regular moves
    # - Captures
    # - Jail releases
    # - Bearing off
```

#### End Game Check
```python
def check_end_game(board):
    # Server verifies:
    # - All pieces cleared
    # - Pieces in home board
    # - Winner determination
```

## Security Implementation

### Encryption Flow
```python
# Message encryption path:
Client -> Router1 (AES) -> Router2 (AES) -> Router3 (AES) -> Server
# Response path:
Server -> Router3 (AES) -> Router2 (AES) -> Router1 (AES) -> Client
```

### Key Management ([keyReader.py](keyReader.py))
```python
def read_keys():
    # Reads encryption keys from files
    key1 = read_key_from_file("key1.bin")
    key2 = read_key_from_file("key2.bin")
    key3 = read_key_from_file("key3.bin")
```

## Communication Protocol

### Message Format
```json
{
    "version": "1",
    "sender": "sender_id",
    "receiver": "receiver_id",
    "type": "message_type",
    "payload": "encrypted_data"
}
```

### Server Commands
- `start game`: Register player
- `request player`: Initiate game request
- `get requests`: Check pending requests
- `roll dice`: Get random dice rolls
- `check end game`: Verify game state

## Usage

1. **Start Network Components**
```bash
python node1.py
python node2.py
python node3.py
python server/server.py
```

2. **Start Client**
```bash
python client.py
```

3. **Game Commands**
```
Enter your Name: [name]
Enter your IP: [ip]

Commands:
- start game
- request player <name>
- get requests
- accept <name>
- roll dice
```

## Dependencies
- Python 3.6+
- MongoDB
- cryptography
- socket
- tkinter (for chat)

## Wireshark Packet Analysis

### Packets Sent by Users via Chat
![Chat Packets](screenshots/chat_packets.png)
Description: This screenshot shows the packets sent by users when they communicate via the P2P chat functionality.

### Packets Sent by User to Router
![User to Router Packets](screenshots/user_to_router_packets.png)
Description: This screenshot captures the packets sent by a user to the first router in the onion routing network.

### Packets Sent Between Routers
![Router to Router Packets](screenshots/router_to_router_packets.png)
Description: This screenshot illustrates the packets exchanged between the routers in the onion routing network.

### Packets Sent Between Users for Game Moves
![Game Move Packets](screenshots/game_move_packets.png)
Description: This screenshot displays the packets sent between users to update the game board and perform moves.

This documentation outlines the core functionality and flow of your Backgammon game, focusing on how the P2P gameplay integrates with the centralized server for game management.