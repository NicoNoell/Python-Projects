import pygame, random

pygame.init()

WALL = -1
EMPTY = 0
START = 1
END = 2
CHECKABLE = 3

screensize = x, y = 800, 800
screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)

def drawText(screen, value, position, size = 25, color = [0, 0, 0]):
        font = pygame.font.SysFont('arial', size)
        text = font.render(str(value), True, color)
        screen.blit(text, position)

class Knoten():
    def __init__(self) -> None:
        self.type = EMPTY
        self.distanceToStart = None
        self.distanceToEnd = None
        self.totalDistance = None
    
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
        elif specialType == CHECKABLE:
            pygame.draw.rect(screen, [255, 220, 255], rect, 0)

        elif self.type == EMPTY:
            pygame.draw.rect(screen, [255, 255, 255], rect, 0)
        elif self.type == WALL:
            pygame.draw.rect(screen, [100, 100, 100], rect, 0)

        pygame.draw.rect(screen, [40, 40, 40], rect, 2)

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
        diagonal = 14 * min(difference[0], difference[1])
        straight = 10 * abs(difference[0]-difference[1])
        self.distanceToEnd = diagonal + straight
        

class Graph():
    def __init__(self, size=(10,10), rect=(0, 0, x, y)) -> None:
        self.size = self.sizeX, self.sizeY = size
        self.rect = rect
        self.knoten = []
        self.start = [1, 1]
        self.end = [8, 8]
        self.knotenToCheck = []
        self.makeGraph()
        self.setupDistances()
    
    def isInBounds(self, x, y):
        if x < 0 or x > self.sizeX-1 or y < 0 or y > self.sizeY-1:
            return False
        return True
    
    def calculateNeighbors(self, x, y):
        for direction in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
            newX, newY = x+direction[0], y+direction[1]
            if self.isInBounds(newX, newY) and self.knoten[newY][newX] != WALL and self.knoten[newY][newX].distanceToStart == None:
                if abs(direction[0]) + abs(direction[1]) == 2:
                    self.knoten[newY][newX].setDistanceToStart(self.knoten[y][x].distanceToStart + 14)
                else:
                    self.knoten[newY][newX].setDistanceToStart(self.knoten[y][x].distanceToStart + 10)
                self.knotenToCheck.append(self.knoten[newY][newX])

    def setupDistances(self):
        self.calculateDistancesToEnd()
        self.knoten[self.start[1]][self.start[0]].setDistanceToStart(0)
        self.calculateNeighbors(self.start[0], self.start[1])

    def makeGraph(self):
        for y in range(self.sizeY):
            row = []
            for x in range(self.sizeX):
                row.append(Knoten())
            self.knoten.append(row)

    def draw(self, screen):
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                width = self.rect[2] / self.sizeX
                height = self.rect[3] / self.sizeY
                rect = [x * width, y * height, width, height]

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

def main():
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False

        draw(screen)

myGraph = Graph()    
main()
pygame.quit()