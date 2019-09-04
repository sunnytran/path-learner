
import math
import pygame
import random
import sys

class Cell:
	def __init__(self, r, c, offset, isGreen=False):
		self.r = r
		self.c = c
		self.offset = offset

		self.isGreen = isGreen
		self.hasAgent = False

	def update(self):
		pass

	def render(self):
		x = self.offset + self.c * gridDrawSize
		y = (h - gridSize * gridDrawSize) / 2 + self.r * gridDrawSize 
		
		pygame.draw.rect(screen, [0] * 3, (x, y, gridDrawSize, gridDrawSize), 1)

		# TODO: find better way
		if self.isGreen:
			qVals = initialQ[self.r * gridSize + self.c]
			if agent.hasPack:
				qVals = dropOffQ[self.r * gridSize + self.c]

			# going clockwise
			# end 1, end 2, pointy
			# TODO: better colors, green too bright
			# TODO: east/west flip flopped?
			pygame.draw.polygon(screen, (
				255 * sigmoid(qVals[0]) if qVals[0] < 0 else 0,
				255 / 1.5 * sigmoid(qVals[0]) if qVals[0] > 0 else 0,
				0), [
				[x, y],
				[x + gridDrawSize, y],
				[x + gridDrawSize/ 2, y + gridDrawSize / 2]
			])
			pygame.draw.polygon(screen, (
				255 * sigmoid(qVals[1]) if qVals[1] < 0 else 0,
				255 / 1.5 * sigmoid(qVals[1]) if qVals[1] > 0 else 0,
				0), [
				[x + gridDrawSize, y],
				[x + gridDrawSize, y + gridDrawSize],
				[x + gridDrawSize / 2, y + gridDrawSize / 2]
			])
			pygame.draw.polygon(screen, (
				255 * sigmoid(qVals[2]) if qVals[2] < 0 else 0,
				255 / 1.5 * sigmoid(qVals[2]) if qVals[2] > 0 else 0,
				0), [
				[x, y + gridDrawSize],
				[x + gridDrawSize, y + gridDrawSize],
				[x + gridDrawSize / 2, y + gridDrawSize / 2]
			])
			pygame.draw.polygon(screen, (
				255 * sigmoid(qVals[3]) if qVals[3] < 0 else 0,
				255 / 1.5 * sigmoid(qVals[3]) if qVals[3] > 0 else 0,
				0), [
				[x, y],
				[x, y + gridDrawSize],
				[x + gridDrawSize / 2, y + gridDrawSize / 2]
			])

			if qVals[0] != 0:
				writtenVal = "{0:.1f}".format(qVals[0])
				text = font.render(writtenVal, True, [255] * 3)
				textRect = text.get_rect()
				textRect = textRect.move((
					x + gridDrawSize / 2 - textRect.w / 2,
					y))
				screen.blit(text, textRect)
			if qVals[1] != 0:
				writtenVal = "{0:.1f}".format(qVals[1])
				text = font.render(writtenVal, True, [255] * 3)
				text = pygame.transform.rotate(text, 90)
				textRect = text.get_rect()
				textRect = textRect.move((
					x + gridDrawSize - textRect.w,
					y + gridDrawSize / 2 - textRect.h / 2))
				screen.blit(text, textRect)
			if qVals[2] != 0:
				writtenVal = "{0:.1f}".format(qVals[2])
				text = font.render(writtenVal, True, [255] * 3)
				textRect = text.get_rect()
				textRect = textRect.move((
					x + gridDrawSize / 2 - textRect.w / 2,
					y + gridDrawSize - textRect.h))
				screen.blit(text, textRect)
			if qVals[3] != 0:
				pass
				writtenVal = "{0:.1f}".format(qVals[3])
				text = font.render(writtenVal, True, [255] * 3)
				text = pygame.transform.rotate(text, -90)
				textRect = text.get_rect()
				textRect = textRect.move((
					x,
					y + gridDrawSize / 2 - textRect.h / 2))
				screen.blit(text, textRect)

class Pickup(Cell):
	def __init__(self, r, c, offset, nPacks):
		super().__init__(r, c, offset, False)
		self.nPacks = nPacks

		self.star = pygame.image.load('star.png').convert_alpha()
		self.star = pygame.transform.scale(self.star, (spriteSize, spriteSize))

	def update(self):
		pass

	def pickUp(self):
		self.nPacks -= 1;

	def render(self):
		super().render()

		x = self.offset + self.c * gridDrawSize
		y = (h - gridSize * gridDrawSize) / 2 + self.r * gridDrawSize 

		rect = self.star.get_rect()
		rect = rect.move((x + spriteSize / 2, y + spriteSize / 2))
		screen.blit(self.star, rect)

		text = font.render(str(self.nPacks), True, [0] * 3)
		textRect = text.get_rect()
		textRect = textRect.move((x + fontSize / 2, y + fontSize / 2))
		screen.blit(text, textRect)

class DropOff(Cell):
	def __init__(self, r, c, offset, nPacks=0):
		super().__init__(r, c, offset, False)
		self.nPacks = nPacks
		self.maxPacks = 5

		self.bin = pygame.image.load('bin.png').convert_alpha()
		self.bin = pygame.transform.scale(self.bin, (spriteSize, spriteSize))

	def update(self):
		pass

	def dropOff(self):
		self.nPacks += 1

	def render(self):
		super().render()

		x = self.offset + self.c * gridDrawSize
		y = (h - gridSize * gridDrawSize) / 2 + self.r * gridDrawSize 

		rect = self.bin.get_rect()
		rect = rect.move((x + spriteSize / 2, y + spriteSize / 2))
		screen.blit(self.bin, rect)

		text = font.render(str(self.nPacks), True, [0] * 3)
		textRect = text.get_rect()
		textRect = textRect.move((x + fontSize / 2, y + fontSize / 2))
		screen.blit(text, textRect)

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

MINSIZE = -sys.maxsize - 1

class Agent():
	def __init__(self, r, c, offset, hasPack=False, reward=0, points=5):
		self.r = r
		self.c = c		
		self.offset = offset

		self.currCell = gridVis[r][c]
		self.currCell.hasAgent = True

		self.hasPack = hasPack
		self.reward = reward
		self.points = points
		self.steps = 0
		self.alpha = 0.3
		self.gamma = 0.5

		self.policy = self.MOVE_RANDOM
		self.method = 0

		self.jack = pygame.image.load('jack.gif').convert_alpha()
		self.jack = pygame.transform.scale(self.jack, (spriteSize, spriteSize))

	def moveable(self, dir):
		if dir == UP:
			return self.r > 0
		if dir == DOWN:
			return self.r < gridSize - 1
		if dir == LEFT:
			return self.c > 0
		if dir == RIGHT:
			return self.c < gridSize - 1

	def getAdjSpecial(self):
		if self.moveable(UP) and (isinstance(gridVis[self.r-1][self.c], Pickup) and not self.hasPack
			or isinstance(gridVis[self.r-1][self.c], DropOff) and self.hasPack):
			return UP
		if self.moveable(RIGHT) and (isinstance(gridVis[self.r][self.c+1], Pickup) and not self.hasPack
			or isinstance(gridVis[self.r][self.c+1], DropOff) and self.hasPack):
			return RIGHT
		if self.moveable(DOWN) and (isinstance(gridVis[self.r+1][self.c], Pickup) and not self.hasPack
			or isinstance(gridVis[self.r+1][self.c], DropOff) and self.hasPack):
			return DOWN
		if self.moveable(LEFT) and (isinstance(gridVis[self.r][self.c-1], Pickup) and not self.hasPack
			or isinstance(gridVis[self.r][self.c-1], DropOff) and self.hasPack):
			return LEFT

		return -1

	def isAdjToSpecial(self):
		return self.getAdjSpecial() != -1

	def move(self, dir):
		if dir == -1:
			return

		if dir == UP:
			self.steps += 1
			return (self.r - 1, self.c)
		if dir == RIGHT:
			self.steps += 1
			return (self.r, self.c + 1)
		if dir == DOWN:
			self.steps += 1
			return (self.r + 1, self.c)
		if dir == LEFT:
			self.steps += 1
			return (self.r, self.c - 1)

	def moveRandom(self):
		if self.isAdjToSpecial():
			newMoveDir = self.getAdjSpecial()
			
			testLoc = self.move(newMoveDir)
			testSpot = gridVis[testLoc[0]][testLoc[1]]
			if isinstance(testSpot, Pickup) and not self.hasPack and testSpot.nPacks > 0:
				updateQ([self.r, self.c], self.alpha, newMoveDir,
					[testSpot.r, testSpot.c], self.gamma, self.hasPack, PICKUP)

				self.r = testLoc[0]
				self.c = testLoc[1]				
				self.points += 13 - 1 # every move -1

				self.currCell = gridVis[self.r][self.c]

				return
			if isinstance(testSpot, DropOff) and self.hasPack and testSpot.nPacks < 5:
				updateQ([self.r, self.c], self.alpha, newMoveDir,
					[testSpot.r, testSpot.c], self.gamma, self.hasPack, DROPOFF)

				self.r = testLoc[0]
				self.c = testLoc[1]
				self.points += 13 - 1
	
				self.currCell = gridVis[self.r][self.c]

				return

		dir = random.randint(0, 3)
		while not self.moveable(dir):
			dir = random.randint(0, 3)
		
		newSpot = self.move(dir)
		updateQ([self.r, self.c], self.alpha, dir, [newSpot[0], newSpot[1]],
			self.gamma, self.hasPack, -1)
		self.r = newSpot[0]
		self.c = newSpot[1]
		self.points -= 1

	def getAdjQs(self):
		vals = [MINSIZE] * 4
		for i in range(0, 4):
			if self.moveable(i):
				coords = self.move(i)

				for j in range(0, 4):
					vals[i] = max(vals[i], getQTableValue(coords, self.hasPack, j))

		res = [vals[UP] if self.moveable(UP) else MINSIZE,
				vals[RIGHT] if self.moveable(RIGHT) else MINSIZE,
				vals[DOWN] if self.moveable(DOWN) else MINSIZE,
				vals[LEFT] if self.moveable(LEFT) else MINSIZE]
		return res

	def getAdjSARSA(self):
		vals = [MINSIZE] * 4
		for i in range(0, 4):
			if self.moveable(i):
				coords = self.move(i)

				vals[i] = getQTableValue(coords, self.hasPack, i)

		res = [vals[UP] if self.moveable(UP) else MINSIZE,
				vals[RIGHT] if self.moveable(RIGHT) else MINSIZE,
				vals[DOWN] if self.moveable(DOWN) else MINSIZE,
				vals[LEFT] if self.moveable(LEFT) else MINSIZE]
		return res

	def findBestMove(self, vals):
		bestVal = MINSIZE
		bestDirs = []

		for i in range(0, len(vals)):
			if vals[i] == bestVal and self.moveable(i):
				bestDirs.append(i)
			if vals[i] > bestVal and self.moveable(i):
				bestVal = vals[i]
				bestDirs = [i]

		return bestDirs[random.randint(0, len(bestDirs) - 1)]

	QLEARN = 0
	SARSA = 1
	def moveExploit(self, method=QLEARN):
		if self.isAdjToSpecial():
			newMoveDir = self.getAdjSpecial()
			
			testLoc = self.move(newMoveDir)
			testSpot = gridVis[testLoc[0]][testLoc[1]]
			if isinstance(testSpot, Pickup) and not self.hasPack and testSpot.nPacks > 0:
				updateQ([self.r, self.c], self.alpha, newMoveDir,
					[testSpot.r, testSpot.c], self.gamma, self.hasPack, 0)

				self.r = testLoc[0]
				self.c = testLoc[1]				
				self.points += 13 - 1 # every move -1

				self.currCell = gridVis[self.r][self.c]

				return
			if isinstance(testSpot, DropOff) and self.hasPack and testSpot.nPacks < 5:
				updateQ([self.r, self.c], self.alpha, newMoveDir,
					[testSpot.r, testSpot.c], self.gamma, self.hasPack, 1)

				self.r = testLoc[0]
				self.c = testLoc[1]
				self.points += 13 - 1
	
				self.currCell = gridVis[self.r][self.c]

				return

		vals = []
		if method == self.QLEARN:
			vals = self.getAdjQs()
		else:
			vals = self.getAdjSARSA()
		bestMove = self.findBestMove(vals)
		
		roll = random.randint(0, 4)
		if roll == 0:
			self.moveRandom()
		else:
			if self.moveable(bestMove):
				updateQ([self.r, self.c], self.alpha, bestMove,
					self.move(bestMove), self.gamma, self.hasPack, -1)
				
				newSpot = self.move(bestMove)
				self.r = newSpot[0]
				self.c = newSpot[1]
				self.points -= 1

	def moveGreedy(self, method=QLEARN):
		if self.isAdjToSpecial():
			newMoveDir = self.getAdjSpecial()
			
			testLoc = self.move(newMoveDir)
			testSpot = gridVis[testLoc[0]][testLoc[1]]
			if isinstance(testSpot, Pickup) and not self.hasPack and testSpot.nPacks > 0:
				updateQ([self.r, self.c], self.alpha, newMoveDir,
					[testSpot.r, testSpot.c], self.gamma, self.hasPack, 0)

				self.r = testLoc[0]
				self.c = testLoc[1]				
				self.points += 13 - 1 # every move -1

				self.currCell = gridVis[self.r][self.c]

				return
			if isinstance(testSpot, DropOff) and self.hasPack and testSpot.nPacks < 5:
				updateQ([self.r, self.c], self.alpha, newMoveDir,
					[testSpot.r, testSpot.c], self.gamma, self.hasPack, 1)

				self.r = testLoc[0]
				self.c = testLoc[1]
				self.points += 13 - 1
	
				self.currCell = gridVis[self.r][self.c]

				return
		
		vals = []
		if method == self.QLEARN:
			vals = self.getAdjQs()
		else:
			vals = self.getAdjSARSA()
		bestMove = self.findBestMove(vals)
		if self.moveable(bestMove):
			updateQ([self.r, self.c], self.alpha, bestMove,
				self.move(bestMove), self.gamma, self.hasPack, -1)

			newSpot = self.move(bestMove)
			self.r = newSpot[0]
			self.c = newSpot[1]
			self.points -= 1

	def checkSpot(self):
		if isinstance(self.currCell, Pickup) and not self.hasPack:
			self.hasPack = True
			self.currCell.pickUp()
		elif isinstance(self.currCell, DropOff) and self.hasPack:
			self.hasPack = False
			self.currCell.dropOff()

	MOVE_RANDOM = 0
	MOVE_EXPLOIT = 1
	MOVE_GREEDY = 2
	def update(self):
		if self.policy == self.MOVE_RANDOM and self.method == 0:
			self.moveRandom()
		else:
			self.moveRandom()
		if self.policy == self.MOVE_EXPLOIT and self.method == 0:
			self.moveExploit()
		else:
			self.moveExploit(1)
		if self.policy == self.MOVE_GREEDY and self.method == 0:
			self.moveGreedy()
		else:
			self.moveGreedy(1)
		self.checkSpot()

	def change_policy(self, num):
		if num == 0:
			self.policy = self.MOVE_RANDOM
		elif num == 1:
			self.policy = self.MOVE_EXPLOIT
		else:
			self.policy = self.MOVE_GREEDY

	def render(self):
		x = self.offset + self.c * gridDrawSize
		y = (h - gridSize * gridDrawSize) / 2 + self.r * gridDrawSize 

		rect = self.jack.get_rect()
		rect = rect.move((x + spriteSize / 2, y + spriteSize / 2))
		screen.blit(self.jack, rect)

		write = str(self.points) + ' points | ' + 'Jack is ' + ('carrying a pack' if self.hasPack else 'not carrying a pack') + '       Steps taken is: ' + str(step_counter) + '         Policy in use is: ' + ('PRANDOM' if self.policy == self.MOVE_RANDOM else 'PEXPLOIT' if self.policy == self.MOVE_EXPLOIT else 'PGREEDY' ) + '          Current Method is: ' + ('Q-Learning' if self.method == 0 else 'SARSA')
		text = font.render(write, True, [0] * 3)
		textRect = text.get_rect()
		textRect = textRect.move(visOffset, (h - gridSize * gridDrawSize) / 2 - fontSize - 4)
		screen.blit(text, textRect)

def isComplete(pickups, dropoffs):
	for i in range(0, len(dropoffs)):
		if dropoffs[i].nPacks != 5:
			return False
	
	for i in range(0, len(pickups)):
		if pickups[i].nPacks != 0:	
			return False

	return True

def getQLoc(loc, hasPack, dir, qLoc=[0,0]):
	j = 5 * loc[0]

	qLoc = [loc[1] + j, dir]
	return qLoc

def getQTableValue(loc, hasPack, dir, qLoc=[0,0]):
	j = 5 * loc[0]

	if not hasPack:
		k = initialQ[loc[1] + j][dir]
	else:
		k = dropOffQ[loc[1] + j][dir]

	qLoc = [loc[1] + j, dir]

	return k

def sigmoid(x):
	return 1 / (1 + math.exp(-x))

PICKUP = 0
DROPOFF = 1
def updateQ(curr, alpha, action, next, gamma, hasPack, reward=-1):
	if reward == PICKUP or reward == DROPOFF:
		reward = 13
	else:
		reward = -1

	currVal = getQTableValue(curr, hasPack, action)
	currLoc = getQLoc(curr, hasPack, action)
	dir = 0
	nextVals = [0, 0, 0, 0]
	newQVal = 0
	for i in range(0, 4):
		nextVals[i] = getQTableValue(curr, hasPack, i)
#	print(nextVals, '        ', next, '         ', agent.r, ', ', agent.c)
	if agent.method == 0:
		newQVal = (1 - alpha) * currVal + alpha * (reward + gamma * max(nextVals))
	elif agent.method == 1:
		if agent.r-1 == next[0]:
			dir = 0
		elif agent.r+1 == next[0]:
			dir = 2
		elif agent.c+1 == next[1]:
			dir = 1
		elif agent.c-1 == next[1]:
			dir = 3
		newQVal = (1 - alpha) * currVal + alpha * (reward + gamma * max(nextVals))
	if not hasPack:
		initialQ[currLoc[0]][currLoc[1]] = newQVal
	else:
		dropOffQ[currLoc[0]][currLoc[1]] = newQVal


def update():
	agent.update()
	for i in range(0, gridSize):
		for j in range(0, gridSize):
			gridVis[i][j].update()
			gridGrn[i][j].update()

def render():
	screen.fill([255] * 3)

	for i in range(0, gridSize):
		for j in range(0, gridSize):
			gridVis[i][j].render()
			gridGrn[i][j].render()
	agent.render()

	pygame.display.update()

def loop():
	delayTime = 50

	#initialRender
	render()
	pygame.time.delay(delayTime)

	while not isComplete(pickups, dropoffs):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()	

		update()
		render()
		pygame.time.delay(delayTime)

def readQTable(fileName):
	file = open(fileName, 'r')
	data = [[ float(n) for n in line.split()] for line in file]
	return data

def reset():
	gridVis[0][0] = Pickup(0, 0, visOffset, 5)
	gridVis[2][2] = Pickup(2, 2, visOffset, 5)
	gridVis[4][4] = Pickup(4, 4, visOffset, 5)
	pickups = [gridVis[0][0], gridVis[2][2], gridVis[4][4]]

	gridVis[1][4] = DropOff(1, 4, visOffset)
	gridVis[4][0] = DropOff(4, 0, visOffset)
	gridVis[4][2] = DropOff(4, 2, visOffset)
	dropoffs = [gridVis[1][4], gridVis[4][0], gridVis[4][2]]

	agent = Agent(0, 4, visOffset)

	return pickups, dropoffs, agent

def write_to_file(filename, top_list):
    with open(filename, 'w') as file:
        file.writelines('\t'.join(str(j) for j in i) + '\n' for i in top_list)

""" Main Begins Here """

random.seed(8) # Seed used for randomization
screenSize = w, h = 1280, 720
gridSize = 5
gridDrawSize = 100

spriteSize = int(gridDrawSize / 2)

pygame.init() #initialize all imported pygame modules
screen = pygame.display.set_mode(screenSize)

# TODO: change this to a windows font that works
fontSize = int(gridDrawSize / 5)
font = pygame.font.SysFont('sourcecodepro', fontSize)

gap = (w - gridSize * gridDrawSize * 2) / 3
visOffset = gap
grnOffset = gap * 2 + gridSize * gridDrawSize
gridVis = [ [Cell(i, j, visOffset) for j in range(0, gridSize)] for i in range(0, gridSize) ]
gridGrn = [ [Cell(i, j, grnOffset, True) for j in range(0, gridSize)] for i in range(0, gridSize) ]

gridVis[0][0] = Pickup(0, 0, visOffset, 5)
gridVis[2][2] = Pickup(2, 2, visOffset, 5)
gridVis[4][4] = Pickup(4, 4, visOffset, 5)
pickups = [ gridVis[0][0], gridVis[2][2], gridVis[4][4] ]

gridVis[1][4] = DropOff(1, 4, visOffset)
gridVis[4][0] = DropOff(4, 0, visOffset)
gridVis[4][2] = DropOff(4, 2, visOffset)
dropoffs = [ gridVis[1][4], gridVis[4][0], gridVis[4][2] ]

agent = Agent(0, 4, visOffset)

initialQ = readQTable('testfile.txt')
dropOffQ = readQTable('testfile2.txt')

# for i in range(0, 3):
# 	if agent.policy != i:
# 		agent.policy = i
# 	for j in range(0, 5000):
# 		loop()
#
# 		resetData = reset()
# 		pickups = resetData[0]
# 		dropoffs = resetData[1]
# 		agent = resetData[2]
#
# 		pygame.time.delay(1000)

delayTime = 50

# initialRender
step = 4000
step_counter = 0
render()
pygame.time.delay(delayTime)
agent.alpha = 0.3
agent.change_policy(0)

# ----------------------EXPERIMENT 1--------------------------------
q=input() 
pointsFile = open("points_file", "w")
stepsFile = open("steps_file", "w")
count1 = step_counter
for i in range(200):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		count1 = step_counter
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)

stepsFile.write("greedy me hoe")
pointsFile.write("greedy me hoe")
agent.change_policy(3)
for i in range(7800):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		agent.change_policy(3)
		count1 = step_counter
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)
	
pointsFile.close()
stepsFile.close()
write_to_file('EXPERIMENT1_withoutBlock.txt', initialQ)
write_to_file('EXPERIMENT1_withBlock.txt', dropOffQ)

pygame.time.delay(5000)
k=input("press close to exit") 

'''
# -----------------------EXPERIMENT 2---------------------------------------
initialQ = readQTable('testfile.txt')
dropOffQ = readQTable('testfile2.txt')
resetData = reset()
pickups = resetData[0]
dropoffs = resetData[1]
agent = resetData[2]
step_counter = 0
agent.change_policy(0)

q=input() 
pointsFile = open("points_file", "w")
stepsFile = open("steps_file", "w")
count1 = step_counter

for i in range(200):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		count1 = step_counter
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)

agent.change_policy(1)

stepsFile.write("exploit me hoe")
pointsFile.write("exploit me hoe")
for i in range(7800):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		agent.change_policy(1)
		count1 = step_counter
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)


write_to_file('EXPERIMENT2_withoutBlock.txt', initialQ)
write_to_file('EXPERIMENT2_withBlock.txt', dropOffQ)
pointsFile.close()
stepsFile.close()
pygame.time.delay(5000)

'''
'''
# -------------------Experiment 3---------------------------------
initialQ = readQTable('testfile.txt')
dropOffQ = readQTable('testfile2.txt')
agent.method = 1 #changes the method to sarsa instead of qlearning update
resetData = reset()
pickups = resetData[0]
dropoffs = resetData[1]
agent = resetData[2]
step_counter = 0
agent.change_policy(0)

q=input() 
pointsFile = open("points_file", "w")
stepsFile = open("steps_file", "w")
count1 = step_counter


for i in range(200):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		agent.method = 1
		count1 = step_counter		
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)

agent.change_policy(1)

stepsFile.write("sarsa me hoe")
pointsFile.write("sarsa me hoe")
for i in range(7800):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		agent.change_policy = 1
		agent.method = 1
		count1 = step_counter
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)

pointsFile.close()
stepsFile.close()
write_to_file('EXPERIMENT3_withoutBlock.txt', initialQ)
write_to_file('EXPERIMENT3_withBlock.txt', dropOffQ)

pygame.time.delay(5000)
'''
'''
# --------------------------EXPERIMENT 4-------------------------------------

initialQ = readQTable('testfile.txt')
dropOffQ = readQTable('testfile2.txt')
agent.method = 1 #changes the method to sarsa instead of qlearning update
resetData = reset()
pickups = resetData[0]
dropoffs = resetData[1]
agent = resetData[2]
step_counter = 0
agent.change_policy(0)
agent.gamma = 1.0
agent.method = 1

q=input() 
pointsFile = open("points_file", "w")
stepsFile = open("steps_file", "w")
count1 = step_counter


for i in range(200):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		agent.method = 1
		count1 = step_counter
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)

agent.change_policy(1)
stepsFile.write("sarsa me hoe")
pointsFile.write("sarsa me hoe")
for i in range(7800):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		agent.change_policy(1)
		agent.method = 1
		count1 = step_counter
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)

pointsFile.close()
stepsFile.close()
write_to_file('EXPERIMENT4_withoutBlock.txt', initialQ)
write_to_file('EXPERIMENT4_withBlock.txt', dropOffQ)

pygame.time.delay(5000)
'''
'''
# --------------------------------EXPERIMENT 5-------------------------------


initialQ = readQTable('testfile.txt')
dropOffQ = readQTable('testfile2.txt')
resetData = reset()
pickups = resetData[0]
dropoffs = resetData[1]
agent = resetData[2]
step_counter = 0
agent.change_policy(0)
terminal_counter = 0
q=input() 
pointsFile = open("points_file", "w")
stepsFile = open("steps_file", "w")
count1 = step_counter
for i in range(200):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		terminal_counter += 1
		count1 = step_counter
		if terminal_counter > 2:
			gridVis[1][4] = Pickup(1, 4, visOffset, 5)
			gridVis[4][0] = Pickup(4, 0, visOffset, 5)
			gridVis[4][2] = Pickup(4, 2, visOffset, 5)
			pickups = [gridVis[1][4], gridVis[4][0], gridVis[4][2]]

			gridVis[0][0] = DropOff(0, 0, visOffset)
			gridVis[2][2] = DropOff(2, 2, visOffset)
			gridVis[4][4] = DropOff(4, 4, visOffset)
			dropoffs = [gridVis[0][0], gridVis[2][2], gridVis[4][4]]
	if terminal_counter == 2:
		gridVis[1][4] = Pickup(1, 4, visOffset, 5)
		gridVis[4][0] = Pickup(4, 0, visOffset, 5)
		gridVis[4][2] = Pickup(4, 2, visOffset, 5)
		pickups = [gridVis[1][4], gridVis[4][0], gridVis[4][2]]

		gridVis[0][0] = DropOff(0, 0, visOffset)
		gridVis[2][2] = DropOff(2, 2, visOffset)
		gridVis[4][4] = DropOff(4, 4, visOffset)
		dropoffs = [gridVis[0][0], gridVis[2][2], gridVis[4][4]]
		terminal_counter += 1

	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)
pygame.time.delay(2000)
agent.change_policy(1)

stepsFile.write("swap my trashcan hoe")
pointsFile.write("swap my trashcann hoe")
for i in range(7800):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	if isComplete(pickups, dropoffs):
		count2 = step_counter;
		diff = count2-count1
		stepsFile.write(str(diff))
		pointsFile.write(str(agent.points))
		stepsFile.write('\n')
		pointsFile.write('\n')
		pygame.time.delay(1000)
		resetData = reset()
		pickups = resetData[0]
		dropoffs = resetData[1]
		agent = resetData[2]
		terminal_counter += 1
		agent.change_policy(1)
		count1 = step_counter
		if terminal_counter > 2:
			gridVis[1][4] = Pickup(1, 4, visOffset, 5)
			gridVis[4][0] = Pickup(4, 0, visOffset, 5)
			gridVis[4][2] = Pickup(4, 2, visOffset, 5)
			pickups = [gridVis[1][4], gridVis[4][0], gridVis[4][2]]

			gridVis[0][0] = DropOff(0, 0, visOffset)
			gridVis[2][2] = DropOff(2, 2, visOffset)
			gridVis[4][4] = DropOff(4, 4, visOffset)
			dropoffs = [gridVis[0][0], gridVis[2][2], gridVis[4][4]]
	if terminal_counter == 2:
		gridVis[1][4] = Pickup(1, 4, visOffset, 5)
		gridVis[4][0] = Pickup(4, 0, visOffset, 5)
		gridVis[4][2] = Pickup(4, 2, visOffset, 5)
		pickups = [gridVis[1][4], gridVis[4][0], gridVis[4][2]]

		gridVis[0][0] = DropOff(0, 0, visOffset)
		gridVis[2][2] = DropOff(2, 2, visOffset)
		gridVis[4][4] = DropOff(4, 4, visOffset)
		dropoffs = [gridVis[0][0], gridVis[2][2], gridVis[4][4]]
		terminal_counter += 1
	step_counter += 1
	update()
	render()
	pygame.time.delay(delayTime)


write_to_file('EXPERIMENT5_withoutBlock.txt', initialQ)
write_to_file('EXPERIMENT5_withBlock.txt', dropOffQ)
pointsFile.close()
stepsFile.close()
pygame.time.delay(5000)
'''
'''
# ---------------END OF EXPERIMENTS----------------------------------------------------

template for creating experiments



while not isComplete(pickups, dropoffs):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

	update()
	render()
	pygame.time.delay(delayTime)

write_to_file('exp1InitQ', initialQ)
write_to_file('exp1DropOffQ', dropOffQ)
pygame.time.delay(1000)
resetData = reset()
pickups = resetData[0]
dropoffs = resetData[1]
agent = resetData[2]

'''
# TODO: Fix greedy
# TODO: SARSA
# TODO: alpha values
# TODO: GUI Text
# TODO: line 430 should be able to input 1 so we can change to sarsa at any time we need in expiriments

# TODO: copy line 610 to 624 5 times for each experiment
# instead of the while loop you may have to do a for loop from 0 to 4000 steps etc
# and have another for loop calling a move function with a method
# like Agent.QLEARN and Agent.SARSA
# make sure u check to break out if complete for each one just in case
# good luck peace out