from board import Board
from network import GameConnection
import random
import sys
from roll_dice import roll_dices
from endgame import check_end_game

#todo: jail rolls
#todo: can't split dice rolls
#todo: make sure the "done" thing works
exitTerms = ("quit", "exit", "bye","q")

def startgame(ip= '127.0.0.1', port= 5555, type ='j'):
    b = Board()
    conn = GameConnection()
    

    
    if type.startswith('h'):
        is_host = True
        conn.host_game(ip, port)
        my_side = True  # Host is X
        print("You are X")
    else:
        is_host = False
        if not conn.join_game(ip, port):
            return
        my_side = False  # Joiner is O
        print("You are O")

    line = ""
    current_side = True  # X starts first
    
    while (line not in exitTerms):
        print(b)
        print("Current turn: " + ("X" if current_side else "O"))
        
        if current_side == my_side:  # My turn
            roll1, roll2 = roll_dices()
            conn.send_move(-1, -1, [roll1, roll2])  # Special move to sync dice rolls
            
            total = roll1 + roll2
            if roll1 == roll2:
                total *= 2
            print(f"You rolled a {roll1} and a {roll2}, giving you a total of {total} moves.")

            while total > 0:
                print(f"You have {total} steps left.")
                line = input("Enter your move: ")
                if line == 'resign':
                    line = input("Do you want to play again?(y/n)\n")
                    if line == "y":
                        print('Sending request to openet..')
                        conn.send_move(-2,-2,[-2,-2])
                        ans = conn.receive_move()
                        if ans['space'] == -4:
                            print("Oponnent accepted! restarting the game..")
                            b = Board()
                            break
                        else:
                            print("game ended")
                            conn.close()
                            return
                    else:
                        conn.send_move(-2,-3,[-2,-2])
                        print("game ended")
                        conn.close()
                        return
                    
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
                    
                    #Check for game end after each move
                    game_over, winner, message = check_end_game(b)
                    print(message)
                    if game_over:
                        print(message)
                        conn.close()
                        return
                        
                    if total == 0:  # No more moves left
                        print("No more moves available. Turn complete.")
                        conn.send_move(100, 100, None)  # Signal end of turn
                        current_side = not current_side

        else:  # Opponent's turn
            print("Waiting for opponent's move...")
            move = conn.receive_move()
            if not move:
                print("Opponent disconnected. Game ended.")
                conn.close()
                return
                
            if move['space'] == -1:  # Receiving dice rolls
                rolls = move['rolls']
                print(f"Opponent rolled a {rolls[0]} and a {rolls[1]}")
            if move['space'] == -2:
                print("YOU WIN! OPPONENT RESIGNED")
                if move['steps'] == -2:
                    ans = input("Oponnent wants a rematch do you agree (y/n)?")
                    if ans == "y":
                        conn.send_move(-4,0,[0,0])
                        b = Board()
                    else:
                        print("Game ended")
                        conn.send_move(-5,0,[0,0])
                        conn.close()
                        return
                else:
                        print("Game ended")
                        conn.close()
                        return

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
    # Check if piece is in jail
    in_jail = (side and board.xJail > 0) or (not side and board.oJail > 0)
    
    if not (0 <= space <= 24):  # Changed from 0-23 to 0-24 to allow for user input of 1-24
        print("Invalid space number. Must be between 1 and 24.")
        return False
    
    if in_jail:
        if space != 0:
            print("You must move from jail first (use 0 as starting position)")
            return False
            
        # Validate the roll first
        if roll1 and roll2 and steps != roll1 and steps != roll2:
            print(f"You must use one of your rolls ({roll1} or {roll2})")
            return False

        # Pass the move directly to board - it will handle the target space calculation
        move, response = board.makeMove(0, side, steps)
        print(response)
        return move
    else:
        # Normal move validation
        if roll1 and roll2:  # Only validate rolls on active player's turn
            if steps != roll1 and steps != roll2 and steps != total and steps != 100:
                print("Invalid move - must use available dice rolls!")
                return False
                
        move, response = board.makeMove(space - 1, side, steps)
        print(response)
        return move

#TODO: Include error management

def parseInput(response):
    print(f"Debug: Parsing input response='{response}'")
    if response in exitTerms:
        return (101, 101)
    loc = findSeparation(response)
    try:
        space = int(response[:loc])
        steps = int(response[loc+1:])
        print(f"Debug: Parsed space={space}, steps={steps}")
        return (space, steps)
    except ValueError:
        print("Debug: Invalid input format.")
        return (-1, -1)

def findSeparation(value):
    for i in range(len(value)):
        if (value[i] == ' ' or value[i] == ','):
            return i
    return 0

if __name__ == "__main__":
    type = input("enter h or j")
    startgame(type=type)