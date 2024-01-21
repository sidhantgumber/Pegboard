import copy

# ---------------------------------------------------------------------------
# JL Popyack, ported to Python, May 2019, updated Nov 2021. v2 Nov 29, 2021
# Ehsan Khosroshahi, updated Nov 2023.
# ---------------------------------------------------------------------------


class PentagoBoard:
#--------------------------------------------------------------------------------
# Basic elements of game:
# Board setup constants, rotation of sectors right (clockwise) or 
# left (counter-clockwise),
# apply a move
#--------------------------------------------------------------------------------

	def __init__ (self,board=""):
	#---------------------------------------------------------------------------
	# board can be a string with 36 characters (w, b, or .) corresponding to the
	# rows of a Pentago Board, e.g., "w.b.bw.w.b.wb.w..wb....w...bw.bbb.ww"
	# Otherwise, the board is empty.
	#---------------------------------------------------------------------------
		self.BOARD_SIZE = 6
		self.GRID_SIZE = 3
		self.GRID_ELEMENTS = self.GRID_SIZE * self.GRID_SIZE

		if board=="":
			self.board = [['.' for col in range(self.BOARD_SIZE)] \
			                   for row in range(self.BOARD_SIZE)]
			self.empty_cells = self.BOARD_SIZE**2
			                   
		else:
			self.board = [[board[row*self.BOARD_SIZE + col] \
			  for col in range(self.BOARD_SIZE)] \
			  for row in range(self.BOARD_SIZE)] 
			self.empty_cells = board.count(".")


	def __str__ (self):
		outstr = "+-------+-------+\n"
		for offset in range(0,self.BOARD_SIZE,self.GRID_SIZE):
			for i in range(0+offset,self.GRID_SIZE+offset):
				outstr += "| "
				for j in range(0,self.GRID_SIZE):
					outstr += str(self.board[i][j]) + " "
				outstr += "| "
				for j in range(self.GRID_SIZE,self.BOARD_SIZE):
					outstr += str(self.board[i][j]) + " "
				outstr += "|\n"
			outstr += "+-------+-------+\n"
		
		return outstr


	def to_string(self):
		return "".join(item for row in self.board for item in row) 


	def get_moves(self):
	#---------------------------------------------------------------------------
	# Determines all legal moves for player with current board,
	# and returns them in moveList.
	#---------------------------------------------------------------------------
		moveList = [ ]
		for i in range(self.BOARD_SIZE):
			for j in range(self.BOARD_SIZE):
				if self.board[i][j] == ".":
				#---------------------------------------------------------------
				#  For each empty cell on the grid, determine its block (1..4)
				#  and position (1..9)  (1..GRID_SIZE^2)
				#---------------------------------------------------------------
					gameBlock = (i // self.GRID_SIZE)*2 + (j // self.GRID_SIZE) + 1
					position  = (i%self.GRID_SIZE)*self.GRID_SIZE + (j%self.GRID_SIZE) + 1
					pos = str(gameBlock) + "/" + str(position) + " "
				#---------------------------------------------------------------
				#  For each block, can place a token in the given cell and
				#  rotate the block either left or right.
				#---------------------------------------------------------------
					numBlocks = (self.BOARD_SIZE // self.GRID_SIZE)**2  # =4 
					for k in range(numBlocks):  
						block = str(k+1)
						moveList.append(pos+block+"L")
						moveList.append(pos+block+"R")

		return moveList

	def rotate_left(self,gameBlock):
	#---------------------------------------------------------------------------
	# Rotate gameBlock counter-clockwise.  gameBlock is in [1..4].
	#---------------------------------------------------------------------------
		rotLeft = copy.deepcopy(self)

		rowOffset = ((gameBlock-1)//2)*self.GRID_SIZE
		colOffset = ((gameBlock-1)%2)*self.GRID_SIZE
		for i in range(0+rowOffset,self.GRID_SIZE+rowOffset):
			for j in range(0+colOffset,self.GRID_SIZE+colOffset):
				rotLeft.board[2-j+rowOffset+colOffset][i-rowOffset+colOffset] = self.board[i][j]

		return rotLeft


	def rotate_right(self,gameBlock):
	#---------------------------------------------------------------------------
	# Rotate gameBlock clockwise.  gameBlock is in [1..4].
	#---------------------------------------------------------------------------
		rotRight = copy.deepcopy(self)

		rowOffset = ((gameBlock-1)//2)*self.GRID_SIZE
		colOffset = ((gameBlock-1)%2)*self.GRID_SIZE
		for i in range(0+rowOffset,self.GRID_SIZE+rowOffset):
			for j in range(0+colOffset,self.GRID_SIZE+colOffset):
				rotRight.board[j+rowOffset-colOffset][2-i+rowOffset+colOffset] = self.board[i][j]

		return rotRight


	def apply_move(self, move, token):
	#---------------------------------------------------------------------------
	# Perform the given move, and update board.
	#---------------------------------------------------------------------------

		gameBlock = int(move[0])  # 1,2,3,4
		position = int(move[2])   # 1,2,3,4,5,6,7,8,9
		rotBlock = int(move[4])   # 1,2,3,4
		direction = move[5]       # L,R

		i = (position-1)//self.GRID_SIZE + self.GRID_SIZE*((gameBlock-1)//2) ;
		j = ((position-1)%self.GRID_SIZE) + self.GRID_SIZE*((gameBlock-1)%2) ;

		newBoard = copy.deepcopy(self)
		newBoard.board[i][j] = token
		
		if( direction=='r' or direction=='R' ):
			newBoard = newBoard.rotate_right(rotBlock) ;
		else: # direction=='l' or direction=='L'
			newBoard = newBoard.rotate_left(rotBlock) ;

		return newBoard


	def get_diagonals(self):
		# Simulate getting all diagonals (not fully implemented)

		return [

			[self.board[i][i] for i in range(self.BOARD_SIZE)],  # Main diagonal

			[self.board[i][self.BOARD_SIZE - i - 1] for i in range(self.BOARD_SIZE)]  # Anti-diagonal

		]


	def is_full(self):
		# Return True if there are no empty cells left on the board
		return all(cell != '.' for row in self.board for cell in row)


