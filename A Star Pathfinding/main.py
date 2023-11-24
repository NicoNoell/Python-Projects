import pygame, random

pygame.init()

WALL = -1
EMPTY = 0
START = 1
END = 2
CHECKABLE = 3
CHECKED = 4
PATH = 5

DRAW_TEXT = False
AUTO_CALCULATE = False
ANIMATION = True
SHOW_CHECKED_KNOTS = True
ALLOW_DIAGONALS = True
size = 20

if ALLOW_DIAGONALS:
    directions = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
else:
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

screensize = x, y = 900, 900
screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
uhr = pygame.time.Clock()

def drawText(screen, value, position, size = 25, color = [0, 0, 0]):
        font = pygame.font.SysFont('arial', size)
        text = font.render(str(value), True, color)
        screen.blit(text, position)

class Knoten():
    def __init__(self, position) -> None:
        self.type = EMPTY
        self.distanceToStart = None
        self.distanceToEnd = None
        self.totalDistance = None
        self.position = self.x, self.y = position
    
    def setDistanceToStart(self, distance):
        self.distanceToStart = distance
        try:
            self.totalDistance = self.distanceToEnd + distance 
        except:
            self.totalDistance = None
    
    def draw(self, screen, rect, specialType = None):
        if specialType == START:
            pygame.draw.rect(screen, [120, 0, 120], rect, 0)
        elif specialType == END:
            pygame.draw.rect(screen, [20, 150, 20], rect, 0)
        elif self.type == PATH:
            pygame.draw.rect(screen, [160, 160, 200], rect, 0)
        elif specialType == CHECKABLE and SHOW_CHECKED_KNOTS:
            pygame.draw.rect(screen, [255, 220, 255], rect, 0)
        elif self.type == CHECKED and SHOW_CHECKED_KNOTS:
            pygame.draw.rect(screen, [230, 140, 230], rect, 0)
        elif self.type == EMPTY:
            pygame.draw.rect(screen, [255, 255, 255], rect, 0)
        elif self.type == WALL:
            pygame.draw.rect(screen, [100, 100, 100], rect, 0)

        pygame.draw.rect(screen, [40, 40, 40], rect, 2)

        if not DRAW_TEXT:
            return

        if self.distanceToEnd == None:
            drawText(screen, "?", (rect[0] + 3, rect[1]))
        else:
            drawText(screen, self.distanceToEnd, (rect[0] + 3, rect[1]))

        if self.distanceToStart == None:
            drawText(screen, "?", (rect[0] + 40, rect[1]))
        else: 
            drawText(screen, self.distanceToStart, (rect[0] + 40, rect[1]))

        if self.totalDistance == None:
            drawText(screen, "?", (rect[0] + 25, rect[1] + 20), 35)
        else: 
            drawText(screen, self.totalDistance, (rect[0] + 15, rect[1] + 30), 35)

    def calculateDistanceToEnd(self, ownPosition, end):
        difference = abs(end[0]-ownPosition[0]), abs(end[1]-ownPosition[1])
        if ALLOW_DIAGONALS:
            diagonal = 14 * min(difference[0], difference[1])
            straight = 10 * abs(difference[0]-difference[1])
            self.distanceToEnd = diagonal + straight
        else:
            self.distanceToEnd = difference[0] * 10 + difference[1] * 10
        

class Graph():
    def __init__(self, size=(10,10), rect=(0, 0, x, y)) -> None:
        self.size = self.sizeX, self.sizeY = size
        self.rect = rect
        self.width = self.rect[2] / self.sizeX
        self.height = self.rect[3] / self.sizeY
        self.knoten = [] #2d-Array with sizeY rows and sizeX columns
        self.start = [1, 1]
        self.end = [size[0]-2, size[1]-2]
        self.knotenToCheck = [] 
        self.pathFound = False
        self.finished = False
        self.makeGraph()
        self.setupDistances()
        if AUTO_CALCULATE:
            self.finish()
    
    def isInBounds(self, x, y):
        if x < 0 or x > self.sizeX-1 or y < 0 or y > self.sizeY-1:
            return False
        return True
    
    def resetPath(self):
        self.knotenToCheck = []
        self.pathFound = False
        self.finished = False
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                knoten = self.knoten[y][x]
                knoten.distanceToEnd = None
                knoten.setDistanceToStart(None)
                if knoten.type != WALL:
                    knoten.type = EMPTY
        
    
    def calculateNeighbors(self, knoten):
        x, y = knoten.position
        for direction in directions:
            newX, newY = x+direction[0], y+direction[1]
            if self.isInBounds(newX, newY):
                newKnoten = self.knoten[newY][newX]
                if newKnoten.type == WALL:
                    continue
                if abs(direction[0]) + abs(direction[1]) == 2:
                    if newKnoten.distanceToStart == None:
                        newKnoten.setDistanceToStart(knoten.distanceToStart + 14)
                        self.knotenToCheck.append(newKnoten)
                    elif knoten.distanceToStart + 14 < newKnoten.distanceToStart:
                        newKnoten.setDistanceToStart(knoten.distanceToStart + 14)
                elif abs(direction[0]) + abs(direction[1]) == 1:
                    if newKnoten.distanceToStart == None:
                        newKnoten.setDistanceToStart(knoten.distanceToStart + 10)
                        self.knotenToCheck.append(newKnoten)
                    elif knoten.distanceToStart + 10 < newKnoten.distanceToStart:
                        newKnoten.setDistanceToStart(knoten.distanceToStart + 10)
                if [newX, newY] == self.end:
                    self.pathFound = True
                    self.finished = True

    def setPath(self):
        if not self.pathFound:
            return
        knoten = self.knoten[self.end[1]][self.end[0]]
        while knoten.distanceToStart > 0:
            bestKnoten = knoten
            for direction in directions:
                newX, newY = knoten.x+direction[0], knoten.y+direction[1]
                if not self.isInBounds(newX, newY):
                    continue
                newKnoten = self.knoten[newY][newX]
                if newKnoten.type == CHECKED and newKnoten.distanceToStart < bestKnoten.distanceToStart:
                    bestKnoten = newKnoten
            bestKnoten.type = PATH
            knoten = bestKnoten
        
    def getTypeWhenClicked(self, pos):
        x, y = int(pos[0] // self.width), int(pos[1] // self.height)
        if not self.isInBounds(x, y):
            return
        return self.knoten[y][x].type

    def setTypeWhenClicked(self, pos, type):
        self.resetPath()
        x, y = int(pos[0] // self.width), int(pos[1] // self.height)
        if not self.isInBounds(x, y):
            return
        self.knoten[y][x].type = type
        self.setupDistances()

    def update(self):
        if self.pathFound or len(self.knotenToCheck) == 0: 
            self.finished = True
            return
        smallest = self.knotenToCheck[0]
        for k in self.knotenToCheck:
            if k.totalDistance < smallest.totalDistance:
                smallest = k
            elif k.totalDistance == smallest.totalDistance and k.distanceToEnd < smallest.distanceToEnd:
                smallest = k
        smallest.type = CHECKED
        self.calculateNeighbors(smallest)
        self.knotenToCheck.remove(smallest)
        self.setPath()

    def finish(self):
        while not self.finished:
            self.update()

    def setupDistances(self):
        self.calculateDistancesToEnd()
        knoten = self.knoten[self.start[1]][self.start[0]]
        knoten.setDistanceToStart(0)
        knoten.type = CHECKED
        self.calculateNeighbors(knoten)

    def makeGraph(self):
        for y in range(self.sizeY):
            row = []
            for x in range(self.sizeX):
                row.append(Knoten((x, y)))
            self.knoten.append(row)

    def draw(self, screen):
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                rect = [x * self.width, y * self.height, self.width, self.height]

                specialType = None
                if [x, y] == self.start:
                    specialType = START
                elif [x, y] == self.end:
                    specialType = END
                elif self.knoten[y][x] in self.knotenToCheck:
                    specialType = CHECKABLE

                self.knoten[y][x].draw(screen, rect, specialType)

        pygame.draw.rect(screen, [0, 0, 0], self.rect, 5)

    def calculateDistancesToEnd(self):
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                self.knoten[y][x].calculateDistanceToEnd((x,y), self.end)

def draw(screen):
    global myGraph
    screen.fill([255, 255, 255])
    myGraph.draw(screen)
    pygame.display.flip()

def start():
    global myGraph
    myGraph = Graph((size, size))  
    draw(screen)

def main():
    global myGraph, size
    start()
    clickedType = None
    
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    myGraph.update()
                    draw(screen)
                elif event.key == pygame.K_UP:
                    if size < 30:
                        size += 5
                    start()
                elif event.key == pygame.K_DOWN:
                    if size > 10:
                        size -= 5
                    start()
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clickedType = myGraph.getTypeWhenClicked(event.pos)
                if clickedType == WALL:
                    clickedType = EMPTY
                else:
                    clickedType = WALL
                myGraph.setTypeWhenClicked(event.pos, clickedType)
                if AUTO_CALCULATE:
                    myGraph.finish()
                    draw(screen)
            elif event.type == pygame.MOUSEMOTION:
                if clickedType != None:
                    myGraph.setTypeWhenClicked(event.pos, clickedType)
                    if AUTO_CALCULATE:
                        myGraph.finish()
                        draw(screen)
            elif event.type == pygame.MOUSEBUTTONUP:
                clickedType = None

        if ANIMATION and not myGraph.finished:
            myGraph.update()
            draw(screen)

        uhr.tick(30)
  
main()
pygame.quit()