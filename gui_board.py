import tkinter as tk
from tkinter import ttk

class BoardGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Backgammon Board")
        
        # Create canvas for the board
        self.canvas = tk.Canvas(self.window, width=800, height=600, bg='forest green')
        self.canvas.pack(pady=20)
        
        # Initialize board graphics
        self._init_board()
        
        # Don't run mainloop in constructor
        self.is_running = True

    def update(self):
        """Safe update method that checks if window still exists"""
        if self.is_running:
            try:
                self.window.update_idletasks()
                self.window.update()
                return True
            except tk.TclError:
                self.is_running = False
                return False
        return False
        
    def on_closing(self):
        self.is_running = False
        self.window.destroy()
        
    def _init_board(self):
        """Initialize the basic board layout"""
        # Draw triangles for each position
        for i in range(24):
            x = (i % 12) * 60 + 50
            y = 50 if i < 12 else 500
            color = 'red' if (i % 2) == 0 else 'black'
            
            if i < 12:
                points = [x, y, x+30, y+100, x+60, y]
            else:
                points = [x, y, x+30, y-100, x+60, y]
            
            self.canvas.create_polygon(points, fill=color, outline='white')
            
        # Draw the center bar
        self.canvas.create_rectangle(380, 50, 420, 550, fill='brown')
        
    def update_board(self, board_state):
        """Update the board display based on the current state"""
        # Clear existing pieces
        self.canvas.delete('piece')
        
        # Draw pieces based on board state
        for space, count in board_state.myBoard.items():
            if count != 0:
                self._draw_pieces(space, count)
                
        # Draw jail pieces
        if board_state.xJail > 0:
            self._draw_jail_pieces('X', board_state.xJail)
        if board_state.oJail > 0:
            self._draw_jail_pieces('O', board_state.oJail)
            
        # Update the window
        self.window.update()
        
    def _draw_pieces(self, space, count):
        """Draw pieces for a specific position"""
        # Calculate position
        x = (space % 12) * 60 + 80
        is_top = space < 12
        
        color = 'white' if count < 0 else 'black'
        count = abs(count)
        
        for i in range(min(count, 5)):  # Show max 5 pieces, stack them
            y = (80 + i*30) if is_top else (470 - i*30)
            self.canvas.create_oval(x-15, y-15, x+15, y+15, 
                                  fill=color, outline='gray', tags='piece')
            
        # If more than 5 pieces, show count
        if count > 5:
            y = 200 if is_top else 400
            self.canvas.create_text(x, y, text=str(count), 
                                  fill='white', font=('Arial', 12), tags='piece')
            
    def _draw_jail_pieces(self, player, count):
        """Draw pieces in jail"""
        x = 400  # Center bar
        start_y = 150 if player == 'X' else 450
        
        for i in range(count):
            y = start_y + (i * 30)
            color = 'black' if player == 'X' else 'white'
            self.canvas.create_oval(x-15, y-15, x+15, y+15, 
                                  fill=color, outline='gray', tags='piece')
