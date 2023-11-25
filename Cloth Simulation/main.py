import pygame, math

pygame.init()
screensize = width, height = 800, 600
screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
uhr = pygame.time.Clock()

GRAVITY = 0.5
POINTSX, POINTSY = 30, 10
FRICTION_WALL = 0.9
FRICTION_CONNECTION = 0.98
MIN_CONNECTION_LENGTH = 20
MAX_CONNECTION_LENGTH = 100
STIFFNESS = 0.1

points = []
connections = []

class Point():
    def __init__(self, pos, fixed=False) -> None:
        self.pos = pos
        self.v = [0, 0]
        self.fixed = fixed
    
    def update(self):
        if not self.fixed:
            self.v[1] += GRAVITY
            self.pos[0] += self.v[0]
            self.pos[1] += self.v[1]
            self.v[0] *= FRICTION_CONNECTION
            self.v[1] *= FRICTION_CONNECTION
            if self.pos[0] < 0:
                self.pos[0] *= -1
                self.v[0] *= -FRICTION_WALL
            elif self.pos[0] > width:
                self.pos[0] = width - (self.pos[0] - width)
                self.v[0] *= -FRICTION_WALL
            if self.pos[1] < 0:
                self.pos[1] *= -1
                self.v[1] *= -FRICTION_WALL
            elif self.pos[1] > height:
                self.pos[1] = height - (self.pos[1] - height)
                self.v[1] *= -FRICTION_WALL

    
    def draw(self, screen):
        if self.fixed:
            pygame.draw.circle(screen, [150, 0, 0], self.pos, 4)
        else:
            pygame.draw.circle(screen, [0, 0, 0], self.pos, 4)

class Connection():
    def __init__(self, point1, point2) -> None:
        self.point1 = point1
        self.point2 = point2

    def diagonalDistance(self):
        distance = self.point2.pos[0] - self.point1.pos[0], self.point2.pos[1] - self.point1.pos[1]
        return math.sqrt(distance[0]**2 + distance[1]**2)
    
    def percentageStreched(self):
        return min(max(0, self.diagonalDistance() - MIN_CONNECTION_LENGTH) / (MAX_CONNECTION_LENGTH - MIN_CONNECTION_LENGTH), 1)

    def checkIfLinesCollide(self, pos1, pos2):
        try:
            x1, y1 = self.point1.pos
            x2, y2 = self.point2.pos
            x3, y3 = pos1
            x4, y4 = pos2
            line1_dx, line1_dy = x2 - x1, y2 - y1
            line2_dx, line2_dy = x4 - x3, y4 - y3
            m = (((x3-x1)/line1_dx) * (line1_dy/line2_dy)  -((y3-y1)/line2_dy))  /  (1-(line2_dx/line1_dx) * (line1_dy/line2_dy))
            n = ((x3-x1)/line1_dx) + m * (line2_dx/line1_dx)
            if m < 0 or m > 1 or n < 0 or n > 1:
                return False
            return True
        except:
            return False
    
    def update(self):
        if self.point1.fixed and self.point2.fixed:
            return
        distance = self.point2.pos[0] - self.point1.pos[0], self.point2.pos[1] - self.point1.pos[1]
        diagonalDistance = self.diagonalDistance()
        if diagonalDistance > MAX_CONNECTION_LENGTH:
            connections.remove(self)
        if diagonalDistance < MIN_CONNECTION_LENGTH:
            return
        force = STIFFNESS * self.percentageStreched()
        if not self.point2.fixed:
            self.point2.v[0] -= distance[0] * force
            self.point2.v[1] -= distance[1] * force
        if not self.point1.fixed:
            self.point1.v[0] += distance[0] * force
            self.point1.v[1] += distance[1] * force

    def draw(self, screen):
        color = int(self.percentageStreched() * 255)
        pygame.draw.line(screen, [color, 0, 0], self.point1.pos, self.point2.pos, 2)

def update():
    for p in points:
        p.update()
    for c in connections:
        c.update()

def draw(screen):
    screen.fill([255, 255, 255])
    for c in connections:
        c.draw(screen)
    for p in points:
        p.draw(screen)
    pygame.display.flip()

def isInPointsBounds(x, y):
    if x < 0 or x > POINTSX-1 or y < 0 or y > POINTSY-1:
        return False
    return True

def start():
    global points, connections
    points = []
    connections = []
    spacing = width / (POINTSX+1)
    for y in range(POINTSY):
        for x in range(POINTSX):
            points.append(Point([(x+1) * spacing, (y+0.5) * spacing], y == 0))
    
    for y in range(POINTSY):
        for x in range(POINTSX):
            point1 = points[y * POINTSX + x]
            for dx, dy in [(1, 0), (0, 1)]:
                if isInPointsBounds(x + dx, y + dy):
                    point2 = points[(y+dy) * POINTSX + x+dx]
                    connections.append(Connection(point1, point2))


def main():
    start()
    lastMousePos = None
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                lastMousePos = event.pos
            elif event.type == pygame.MOUSEMOTION:
                if lastMousePos == None:
                    continue
                for c in connections:
                    if c.checkIfLinesCollide(lastMousePos, event.pos):
                       connections.remove(c)
                       pass
                lastMousePos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if lastMousePos == None:
                    continue
                for c in connections:
                    if c.checkIfLinesCollide(lastMousePos, event.pos):
                        connections.remove(c)
                        pass
                lastMousePos = None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    start()
            


        update()
        draw(screen)

        uhr.tick(30)
        
main()
pygame.quit() 