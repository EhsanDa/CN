from board import Board
from network import GameConnection
import random
import sys

#todo: jail rolls
#todo: can't split dice rolls
#todo: make sure the "done" thing works
exitTerms = ("quit", "exit", "bye","q")

def main():
    b = Board()
    conn = GameConnection()
    
    print("Do you want to (h)ost or (j)oin a game?")
    choice = input().lower()
    
    if choice.startswith('h'):
        is_host = True
        conn.host_game()
        my_side = True  # Host is X
        print("You are X")
    else:
        is_host = False
        host_ip = input("Enter host IP address: ")
        if not conn.join_game(host_ip):
            return
        my_side = False  # Joiner is O
        print("You are O")

    line = ""
    current_side = True  # X starts first
    
    while (line not in exitTerms and (b.xFree < 15 or b.oFree < 15)):
        print(b)
        print("Current turn: " + ("X" if current_side else "O"))
        
        if current_side == my_side:  # My turn
            roll1 = random.randint(1, 6)
            roll2 = random.randint(1, 6)
            conn.send_move(-1, -1, [roll1, roll2])  # Special move to sync dice rolls
            
            total = roll1 + roll2
            if roll1 == roll2:
                total *= 2
            print(f"You rolled a {roll1} and a {roll2}, giving you a total of {total} moves.")

            while total > 0:
                print(f"You have {total} steps left.")
                line = input("Enter your move: ")
                space, steps = parseInput(line)
                
                if space == 100 and steps == 100:  # "done" command
                    print("Ending turn.")
                    conn.send_move(100, 100, None)  # Signal end of turn
                    current_side = not current_side
                    break
                    
                if space == 101 and steps == 101:  # Exit game
                    conn.close()
                    return

                if make_valid_move(b, my_side, space, steps, roll1, roll2, total):
                    conn.send_move(space, steps, None)
                    total -= steps
                    print(b)
                    if total == 0:  # No more moves left
                        print("No more moves available. Turn complete.")
                        conn.send_move(100, 100, None)  # Signal end of turn
                        current_side = not current_side

        else:  # Opponent's turn
            print("Waiting for opponent's move...")
            move = conn.receive_move()
            if not move:
                continue
                
            if move['space'] == -1:  # Receiving dice rolls
                rolls = move['rolls']
                print(f"Opponent rolled a {rolls[0]} and a {rolls[1]}")
            elif move['space'] == 100:  # Turn complete
                print("Opponent's turn is complete.")
                current_side = not current_side
            else:  # Normal move
                make_valid_move(b, not my_side, move['space'], move['steps'], None, None, None)
                print(b)

    conn.close()

def make_valid_move(board, side, space, steps, roll1, roll2, total):
    """
    Validate and apply a move on the board.
    Returns True if move was valid, False otherwise.
    """
    if roll1 and roll2:  # Only validate rolls on active player's turn
        if steps != roll1 and steps != roll2 and steps != (roll1 + roll2) and steps != 100:
            print("You didn't roll that!")
            return False
            
    move, response = board.makeMove(space - 1, side, steps)  # Apply move
    print(response)
    return move

#TODO: Include error management
def parseInput(response):
    if response == "d" or response == "f" or response == "done" or response == "finish":
        return(100,100)
    if response in exitTerms:
        return (101, 101)
    # if type(response) == type("Sample string"):
    #     return(101,101)
    loc = findSeparation(response)
    return(int(response[:loc]), int(response[loc+1:])) 

def findSeparation(value):
    for i in range(len(value)):
        if (value[i] == ' ' or value[i] == ','):
            return i
    return 0

if __name__ == "__main__":
    main()