class Board:
	def __init__(self):
		self.myBoard = {}
		for i in range(24):
			self.myBoard[i] = 0
		self.myBoard[0] = 2
		self.myBoard[5] = -5
		self.myBoard[7] = -3
		self.myBoard[11] = 5
		self.myBoard[12] = -5
		self.myBoard[16] = 3
		self.myBoard[18] = 5
		self.myBoard[23] = -2
		self.maxRows = 5
		self.xFree = 0
		self.oFree = 0
		self.xJail = 0
		self.oJail = 0
		self.xHome = 5
		self.oHome = 5
	
	def makeMove(self, space, side, steps):
		"""
		Updated makeMove function with corrected jail release mechanics
		"""
		print(f"Debug: makeMove called with space={space}, side={'X' if side else 'O'}, steps={steps}")
		print(f"Debug: Current xJail={self.xJail}, oJail={self.oJail}")

		# Handle jail releases
		if (side and self.xJail > 0) or (not side and self.oJail > 0):
			valid, message = self.validate_jail_release(side, 0, steps)  # Always use 0 for jail moves
			if not valid:
				return (False, message)
			
			if side:  # X's turn
				target_space = 24 - steps - 1  # Subtract 1 because array is 0-based
				if not (18 <= target_space <= 23):
					return (False, "Invalid dice roll for jail release")
					
				self.xJail -= 1
				if self.myBoard[target_space] == 1:
					self.myBoard[target_space] = -1
					self.oJail += 1
					self.oHome -= 1
					return (True, f"Piece released from jail to {target_space + 1} and opponent sent to jail!")
				else:
					self.myBoard[target_space+1] -= 1
					return (True, f"Piece released from jail to {target_space}!")
			else:  # O's turn
				target_space = steps - 1
				if not (0 <= target_space <= 5):
					return (False, "Invalid dice roll for jail release")
					
				self.oJail -= 1
				if self.myBoard[target_space] == -1:
					self.myBoard[target_space] = 1
					self.xJail += 1
					self.xHome -= 1
					return (True, f"Piece released from jail to {target_space + 1} and opponent sent to jail!")
				else:
					self.myBoard[target_space] += 1
					return (True, f"Piece released from jail to {target_space + 1}!")

		# Handle normal moves (when no pieces are in jail)
		if side:  # X's turn
			if self.myBoard[space] >= 0:
				return (False, "Space is either empty or contains opponent pieces.")
			newSpace = space - steps
			if newSpace < 0:  # Clearing pieces
				if self.xHome < 15:
					return (False, "Make sure all your pieces are in the home before clearing them!")
				else:
					self.myBoard[space] += 1
					self.xFree += 1
					return (True, "Piece cleared!")
			if self.myBoard[newSpace] > 1:
				return (False, "New space is occupied by opponent pieces.")
			elif self.myBoard[newSpace] == 1:
				self.myBoard[space] += 1
				self.myBoard[newSpace] = -1
				self.oJail += 1
				if newSpace >= 18:
					self.oHome -= 1
				return (True, "Sent one opponent piece to jail!")
			else:
				self.myBoard[space] += 1
				self.myBoard[newSpace] -= 1
				if newSpace < 6:
					self.xHome += 1
				return (True, "Move made successfully.")
		else:  # O's turn
			if self.myBoard[space] <= 0:
				return (False, "Space is either empty or contains opponent pieces.")
			newSpace = space + steps
			if newSpace > 23:  # Clearing pieces
				if self.oHome < 15:
					return (False, "Make sure all your pieces are in the home before clearing them!")
				else:
					self.myBoard[space] -= 1
					self.oFree += 1
					return (True, "Piece cleared!")
			if self.myBoard[newSpace] < -1:
				return (False, "New space is occupied by opponent pieces.")
			elif self.myBoard[newSpace] == -1:
				self.myBoard[space] -= 1
				self.myBoard[newSpace] = 1
				self.xJail += 1
				if newSpace < 6:
					self.xHome -= 1
				return (True, "Sent one opponent piece to jail!")
			else:
				self.myBoard[space] -= 1
				self.myBoard[newSpace] += 1
				if newSpace > 17:
					self.oHome += 1
				return (True, "Move made successfully.")

		
	def updateRows(self, top):
		changed = False
		if top:
			for i in range(12):
				if (self.myBoard[i] > 5):
					self.maxRows = self.myBoard[i]
					changed = True
		else:
			for i in range(23,11,-1):
				if (self.myBoard[i] > 5):
					self.maxRows = self.myBoard[i]
					changed = True
		if not changed:
			self.maxRows = 5


	def validate_jail_release(self, side, space, steps):
		"""
		Validate jail release moves according to backgammon rules.
		space should be 0 when attempting jail release.
		X starts from 24, O starts from 1
		"""
		if space != 0:
			return (False, "Jail release must start with space 0")

		if side:  # X's turn
			if self.xJail > 0:
				target_space = 24 - steps - 1  # Subtract 1 for 0-based array
				if 18 <= target_space <= 23:  # Valid range for X's reentry
					if self.myBoard[target_space] > 1:
						return (False, "Target space is occupied by multiple opponent pieces")
					return (True, f"Valid jail release move for X to space {target_space + 1}")
				return (False, "Invalid dice roll for jail release")
		else:  # O's turn
			if self.oJail > 0:
				target_space = steps - 1
				if 0 <= target_space <= 5:  # Valid range for O's reentry
					if self.myBoard[target_space] < -1:
						return (False, "Target space is occupied by multiple opponent pieces")
					return (True, f"Valid jail release move for O to space {target_space + 1}")
				return (False, "Invalid dice roll for jail release")
		
		return (False, "No pieces in jail")


	def __repr__(self):
		"""
		1 -> 1
		2 -> 5
		3 -> 9
		4 -> 13
		5 -> 17
		6 -> 21
		7 -> 28
		8 -> 32
		9 -> 36
		10 -> 40
		11 -> 44
		12 -> 48
		13 -> 1
		17 -> 17
		19 -> 28
		24 -> 48
		"""

		emptyline = "|                       | |                       |"
		if (self.oJail > 0):
			boardstring = "					O Jail: " + str(self.oJail) + "\n"
			boardstring += "				X HOME BOARD 	Freed:" + str(self.xFree) + "\n"
		else:
			boardstring = "				X HOME BOARD 	Freed:" + str(self.xFree) + "\n"
		boardstring += " -------------------------------------------------\n"
		boardstring += "|12  11  10  9   8   7  | | 6   5   4   3   2   1 |\n"
		for i in range(self.maxRows):
			boardstring += self.populateTop(i)
		boardstring += " ------------------------------------------------- \n"
		for i in range(self.maxRows-1,-1,-1):
			boardstring += self.populateBottom(i)
		boardstring += "|13  14  15  16  17  18 | | 19  20  21  22  23  24|\n"
		boardstring += " -------------------------------------------------\n"
		boardstring += "				O HOME BOARD 	Freed: " + str(self.oFree) + "\n"
		if (self.xJail > 0):
			boardstring += "					X Jail: " + str(self.xJail) + "\n"
		return boardstring
		

	def populateTop(self, lineNumber):
		"""
		1 -> 1
		2 -> 5
		3 -> 9
		4 -> 13
		5 -> 17
		6 -> 21
		7 -> 28
		8 -> 32
		9 -> 36
		10 -> 40
		11 -> 44
		12 -> 48
		"""
		line = "|                       | |                       |\n"
		boardtostring = {} 
		boardtostring[0] = 48
		boardtostring[1] = 44
		boardtostring[2] = 40
		boardtostring[3] = 36
		boardtostring[4] = 32
		boardtostring[5] = 28
		boardtostring[6] = 21
		boardtostring[7] = 17
		boardtostring[8] = 13
		boardtostring[9] = 9
		boardtostring[10] = 5
		boardtostring[11] = 1
		for i in range(12):
			if (self.myBoard[i] > lineNumber):
				line = line[:boardtostring[i]] + 'O' + line[boardtostring[i]+1:]
			elif (abs(self.myBoard[i]) > lineNumber and self.myBoard[i] < 0):
				line = line[:boardtostring[i]] + 'X' + line[boardtostring[i]+1:]
		return line

	def populateBottom(self, lineNumber):
		line = "|                       | |                       |\n"
		boardtostring = {}
		boardtostring[11] = 48
		boardtostring[10] = 44
		boardtostring[9] = 40
		boardtostring[8] = 36
		boardtostring[7] = 32
		boardtostring[6] = 28
		boardtostring[5] = 21
		boardtostring[4] = 17
		boardtostring[3] = 13
		boardtostring[2] = 9
		boardtostring[1] = 5
		boardtostring[0] = 1
		for i in range(12):
			if (self.myBoard[12+i] > lineNumber):
				line = line[:boardtostring[i]] + 'O' + line[boardtostring[i]+1:]
			elif (abs(self.myBoard[12+i]) > lineNumber and self.myBoard[12+i] < 0):
				line = line[:boardtostring[i]] + 'X' + line[boardtostring[i]+1:]
		return line
	
	
	def has_valid_moves(self, side, roll1, roll2):
		"""
		Check if the player has any valid moves left.
		"""
		for space in range(24):
			if self.myBoard[space] == 0:
				continue  # Skip empty spaces

			if side and self.myBoard[space] < 0:  # X's pieces
				if self.is_valid_move(space, side, roll1) or self.is_valid_move(space, side, roll2):
					return True
			elif not side and self.myBoard[space] > 0:  # O's pieces
				if self.is_valid_move(space, side, roll1) or self.is_valid_move(space, side, roll2):
					return True

		return False

	def is_valid_move(self, space, side, steps):
		"""
		Check if a move from the given space with the given steps is valid.
		"""
		if steps == 0:
			return False

		if side:  # X's turn
			new_space = space - steps
			if new_space < 0:  # Clearing pieces
				return self.xHome >= 15
			return self.myBoard[new_space] <= 1  # Valid if empty or one opponent's piece
		else:  # O's turn
			new_space = space + steps
			if new_space > 23:  # Clearing pieces
				return self.oHome >= 15
			return self.myBoard[new_space] >= -1  # Valid if empty or one opponent's piece

	def debug_board_status(self):
		print(f"Debug: xJail={self.xJail}, oJail={self.oJail}")
		print(f"Debug: xHome={self.xHome}, oHome={self.oHome}")
		print(f"Debug: xFree={self.xFree}, oFree={self.oFree}")
		print("Debug: Board State:")
		for i in range(24):
			print(f"Space {i}: {self.myBoard[i]}")
