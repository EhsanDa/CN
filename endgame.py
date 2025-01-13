def check_game_end(board):
    """
    Check if the game has ended based on Backgammon rules.
    Returns (is_game_over, winner, message)
    winner: True for X, False for O, None if game not over
    """
    # Check if X has won
    if board.xFree == 15:
        return (True, True, "X wins! All pieces cleared!")
    
    # Check if O has won
    if board.oFree == 15:
        return (True, False, "O wins! All pieces cleared!")
        
    # Check if all X pieces are in home or freed
    x_in_home = True
    for i in range(6, 24):  # Check all spaces outside X's home
        if board.myBoard[i] < 0:  # Found X piece outside home
            x_in_home = False
            break
            
    # Check if all O pieces are in home or freed
    o_in_home = True
    for i in range(0, 18):  # Check all spaces outside O's home
        if board.myBoard[i] > 0:  # Found O piece outside home
            o_in_home = False
            break
    
    # Return game state
    if x_in_home and o_in_home:
        # If both players are in their home boards, compare freed pieces
        if board.xFree > board.oFree:
            return (True, True, "X wins with more pieces freed!")
        elif board.oFree > board.xFree:
            return (True, False, "O wins with more pieces freed!")
            
    # Game continues
    return (False, None, "Game continues")
