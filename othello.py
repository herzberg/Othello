import random
import time

inf = 100000
boardCount = 100000
boardPointer = 0
allBoards = []			

def main():
	board = Board()
	humanPlayers = []
	while(not board.over()):
		moves = board.moves()
		board.show()
		print("Player %s:" % board.sym()) 
		if board.player in humanPlayers:
			moveNum = getMoveFromHuman(board,moves)
		else:
			moveNum = getMoveFromComp(board,moves)
		move = moves[moveNum]
		board.goto(move)
	print("final board:",board.score(), board.winnner())
	board.show()
	

def getMoveFromHuman(board,moves):
	board.show(moves)
	if(moves == [(-1,-1)]):
		print("You have no legal move... other player's turn")
		return 0
	board.printMoves(moves)
	moveNum = -1
	while(moveNum < 0 or moveNum > len(moves)-1):
		moveNum = input("select valid move:")
		try:
			moveNum = int(moveNum)
		except:
			moveNum = -1
	return moveNum
	
startDepth = 4
def getMoveFromComp(board,moves):
	depth =  startDepth if board.player == -1 else startDepth
	alpha,beta = -inf,inf
	board.show(moves)
	board.printMoves(moves)
	boardPointer = 0
	start_time = time.time()
	val,moveNum = alphabeta(board, depth, alpha,beta, True)
	print("--- %s seconds to depth %s ---" % ((time.time() - start_time),depth))
	print("alphabeta: " , val,moveNum)
	return moveNum #random.randint(0,len(moves)-1)

	
def alphabeta(board, depth, alpha, beta, maxPlayer):
	remDepth = startDepth - depth
	if(depth == 0 or board.over()):
		h = board.heuristic()
		print("\t"*remDepth + "heuristic: %s" %h)
		print(board.show())
		return h,-1
		
	moves = board.moves()
	moveNum = 0
	if maxPlayer:
		val = -inf
		for i,move in enumerate(moves):
			print("\t"*remDepth,"val:", val,"player:", board.player, "move:", move, "alpha:", alpha,"beta:",beta)
			#print(board.show())
			childBoard = board.child(move)
			temp = alphabeta(childBoard,depth-1,alpha,beta,False)[0]
			if(temp>val):
				val = temp
				moveNum = i
			alpha = max(alpha,val)
			if beta <= alpha:
				break
	else: #min
		val = inf
		for i,move in enumerate(moves):
			print("\t"*remDepth,"val:", val,"player:", board.player, "move:", move, "alpha:", alpha,"beta:",beta)
			#print(board.show())
			childBoard = board.child(move)
			temp = alphabeta(childBoard,depth-1,alpha,beta,True)[0]
			if(temp<val):
				val = temp
				moveNum = i
			beta = min(beta,val)
			if(beta <= alpha):
				break

	
	return val,moveNum
			

	
	
class Board:
	N = 8 # board size is N by N
	directions = []
	for a in range(-1,2):
		for b in range(-1,2):
			if(a == b and a == 0):
				continue
			directions.append((a,b))		
	cornerVal = 5
	hBoard = [
		[cornerVal,-3,2,2,2,2,-3,cornerVal],
		[-3,-4,-1,-1,-1,-1,-4,-3],
		[2,-1,1,0,0,1,-1,2],
		[2,-1,0,1,1,0,-1,2],
		[2,-1,0,1,1,0,-1,2],
		[2,-1,1,0,0,1,-1,2],
		[-3,-4,-1,-1,-1,-1,-4,-3],
		[cornerVal,-3,2,2,2,2,-3,cornerVal]
	]
	
	cornerVal = 5
	hBoardOld = [
		[cornerVal,-3,2,2,2,2,-3,cornerVal],
		[-3,-4,-1,-1,-1,-1,-4,-3],
		[2,-1,1,0,0,1,-1,2],
		[2,-1,0,1,1,0,-1,2],
		[2,-1,0,1,1,0,-1,2],
		[2,-1,1,0,0,1,-1,2],
		[-3,-4,-1,-1,-1,-1,-4,-3],
		[cornerVal,-3,2,2,2,2,-3,cornerVal]
	]
			
	def __init__(self):
		self.b = [[0]*Board.N for _ in range(Board.N)]
		self.spots = 0
		self.default()
		self.skippedLastTurn = False
		self.player = 1
			
	def score(self):
		sum = 0
		for row in self.b:
			for val in row:
				sum += val
		return sum
		
	def sym(self,player = 0):
		if(player == 0):
			player = self.player
		return '@' if player == -1 else '#'
		
	def winnner(self):
		return '@' if self.score() < 0 else '#'
			
		
	def heuristic(self):
		if self.over():
			#print("over!!")
			sum = self.score()
			winning = 1000 if (sum > 0) else -1000
			winning += sum
			winning = self.player*winning
			return winning
		
		sum = 0
		"""
		for y,row in enumerate(self.b):
			for x,val in enumerate(row):
				sum += Board.hBoard[y][x]*val
		"""	
		corners = [(0,0),(0,7),(7,0),(7,7)]
		
		
		#sides*3 with corners *6
		sidePoints = 50
		for i in range(Board.N):
			sum += sidePoints*(self.b[i][0] + self.b[i][7] + self.b[0][i] + self.b[7][i])
		for corner in corners:
			y,x = corner
			sum += self.b[y][x]*sidePoints*4
		
		
		badPoints = round(sidePoints*1.5)
		#subcorners bad
		
		for corner in corners:
			y,x = corner
			if(self.b[y][x] != 0):
				continue
			for dir in Board.directions:
				a,b = y+dir[0],x+dir[1]
				if(a<0 or b<0 or b>7 or a>7):continue
				sum -= badPoints*self.b[a][b] #it's bad to have things next to 
					#sum -= 5*(self.b[1][1] + self.b[1][6]+ self.b[6][1]+ self.b[6][6])
		
		ratio = self.spots/64
		
		sum = self.score()*ratio + (1-ratio)*sum
			
		return sum*self.player
			
	
	def default(self):
		self.b[4][4] = -1
		self.b[4][3] = 1
		self.b[3][3] = -1
		self.b[3][4] = 1
		self.spots = 4
		
	def over(self):
		return self.spots >= 64
	
	def goto(self,move,predicting = False):
		#assuming it's a valid move based on previous checks
		if(move == (-1,-1)):
			if not predicting: print("skipping turn")
			if(self.skippedLastTurn):
				self.spots = 100 # end the game
			self.skippedLastTurn = True
			self.player = -self.player
			return
		self.skippedLastTurn = False
		y,x = move
		if not predicting:
			print("Going to: %s,%s" % (y,x))
		self.b[y][x] = self.player
		self.spots += 1
		for dir in Board.directions:
			#print("dir",dir)
			try:
				a,b = y+dir[0],x+dir[1]
				#print("\ta,b - in try", a,b)
				if(a<0 or b<0):continue
				while(self.b[a][b] == -self.player):
					#print("\t\ta,b - in while1", a,b)
					a,b = a+dir[0],b+dir[1]
					if(a<0 or b<0):break
					if(self.b[a][b] == self.player):
						while(a != y or b!=x):#fill in those spots
							#print("\t\t\ta,b - in while2", a,b)
							a,b = a-dir[0],b-dir[1]
							if(a<0 or b<0):break
							self.b[a][b] = self.player
						break
			except:#went off the edge of the board
				pass
				#print("EXCEPT")
		self.player = -self.player
		return
		
	def child(self,move):
		"""
		global boardPointer
		global boardCount
		global allBoards
		if(boardPointer >= boardCount):
			allBoards += [ Board() for i in range(1000)]
			boardCount += 1000
		boardPointer += 1
		"""
		childBoard = Board() #allBoards[boardPointer]
		
		childBoard.spots = self.spots
		childBoard.skippedLastTurn = self.skippedLastTurn
		childBoard.player = self.player
		for y,row in enumerate(self.b):
			for x,val in enumerate(row):
				childBoard.b[y][x] = val
		childBoard.goto(move,True)
		#print("child num " ,i)
		#childBoard.show()
		return childBoard
		
		
	def show(self,moves=[]):
		space = "   "
		print("\n   0%s1%s2%s3%s4%s5%s6%s7%s" %(space,space,space,space,space,space,space,space),end='')
		line = "  --------------------------------"
		for y,row in enumerate(self.b):
			print("\n%s"%line)
			print("%s|"%y,end='')
			for x,num in enumerate(row):
				sym = '   |'
				if num !=0:
					sym = ' %s |' % self.sym(num)
				else:
					move = (y,x)
					for i,valMoves in enumerate(moves):
						if move == valMoves:
							if i < 10:
								sym = ' %s |' % i
							else:
								sym = ' %s|' % i
							break
				print(sym,end='')
		print("\n%s\n" %line)
		
		
	def trySpot(self,y,x):
		if(self.b[y][x] != 0):
			return False
		for dir in Board.directions:
			try:
				a,b = y+dir[0],x+dir[1]
				if(a<0 or b<0):continue
				if(self.b[a][b] == -self.player):
					#there's the enemy peice next to an empty spot
					while(True):					
						a,b = a+dir[0],b+dir[1]
						if(a<0 or b<0):break
						if(self.b[a][b] == self.player):
							return True
			except:#went off the edge of the board
				pass
				
				
		return False
	def moves(self):
		valMoves = []
		for y in range(Board.N):
			for x in range(Board.N):
				if(self.trySpot(y,x)):
					valMoves.append((y,x))
		if(len(valMoves) == 0):
			valMoves.append((-1,-1))
					
		
		return valMoves
	def printMoves(self,moves):
		for i,move in enumerate(moves):
			print("%s.%s" %(i,move))

allBoards = [ Board() for i in range(boardCount)]			
print("made boards")
	
if __name__ == "__main__":
	start_time = time.time()
	main()
	print("--- %s seconds ---" % (time.time() - start_time))
	print(boardPointer)
	
	