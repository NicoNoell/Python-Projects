import pygame
import random
import math
import multiprocessing as mp

FRICTION = 0.98
FRICTION_THRESHOLD = 1 # Speed required for friction to be applied
BOOST = 0.2
BOOST_THRESHOLD = 0.1
FISHSCALING = 1.25

def vectorLength(vector2d):
    return math.sqrt(vector2d[0]**2 + vector2d[1]**2)

def angleBetweenVectors(v1, v2):
    angle = math.acos((v1[0] * v2[0] + v1[1] * v2[1]) / (vectorLength(v1) * vectorLength(v2)))
    if (v1[0] * v2[1] - v1[1] * v2[0]) > 0: # Get direction of rotation over cross-produkt (Not fully understood yet but it works)
        return 2*math.pi - angle
    return angle 

def randomScreenPos(screensize):
    return [random.randint(0, screensize[0]), random.randint(0, screensize[1])]

def normalize(vector2d):
    length = vectorLength(vector2d)
    return (vector2d[0] / length, vector2d[1] / length)

def polarToKartesian(length, rot):
    return (math.cos(rot) * length, -math.sin(rot) * length)

def distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

class Fish():
    def __init__(self, screensize, viewwidth = 1, viewlength = 300):
        self.pos = randomScreenPos(screensize)
        self.vel = [random.random() * 2 - 1, random.random() * 2 - 1]
        self.rot = self.getRot()
        self.nextpos = self.pos
        self.nextvel = self.vel

        self.viewwidth = viewwidth
        self.viewlength = viewlength

    def getRot(self):
        if self.vel == [0, 0]:
            return 0
        
        angle = angleBetweenVectors((1, 0), self.vel)
        return angle 

    def draw(self, screen, fishcolor = [150, 150, 255], fishsize = 1):
        # self.drawFov(screen)
        # self.drawVelLine(screen)

        points = [(8, 0), (6, 2.3), (1, math.pi), (6, -2.3)] # Points have the form (length, angle) [polar coordinates]
        newPoints = []
        for point in points:
            rotatedPoint = polarToKartesian(point[0] * fishsize, point[1] + self.rot)
            newPoints.append((self.pos[0] + rotatedPoint[0], self.pos[1] + rotatedPoint[1]))
        pygame.draw.polygon(screen, fishcolor, newPoints)

    def drawFov(self, screen):
        pygame.draw.arc(screen, [0, 255, 100], [self.pos[0] - self.viewlength, self.pos[1] - self.viewlength, 2 * self.viewlength, 2 * self.viewlength], self.rot - self.viewwidth/2, self.rot + self.viewwidth/2, 1)
        leftPoint = polarToKartesian(self.viewlength, self.rot - self.viewwidth/2)
        rightPoint = polarToKartesian(self.viewlength, self.rot + self.viewwidth/2)
        pygame.draw.line(screen, [0, 255, 100], self.pos, [self.pos[0] + leftPoint[0], self.pos[1] + leftPoint[1]], 1)
        pygame.draw.line(screen, [0, 255, 100], self.pos, [self.pos[0] + rightPoint[0], self.pos[1] + rightPoint[1]], 1)


    def drawVelLine(self, screen):
        pygame.draw.line(screen, [255, 0, 0], self.pos, [self.pos[0] + 20*self.vel[0], self.pos[1] + 20*self.vel[1]], 1)

    def isInFov(self, fish):
        # toFishVector = (fish.pos[0] - self.pos[0], fish.pos[1] - self.pos[1])
        # if math.sqrt((fish.pos[0] - self.pos[0])*(fish.pos[0] - self.pos[0]) + (fish.pos[1] - self.pos[1])*(fish.pos[1] - self.pos[1])) > self.viewlength:
        if abs(fish.pos[0] - self.pos[0]) > self.viewlength or abs(fish.pos[1] - self.pos[1]) > self.viewlength:
            return False
        
        try:
            angle = angleBetweenVectors((fish.pos[0] - self.pos[0], fish.pos[1] - self.pos[1]), self.vel) # Value between 0 and 2Pi
        except Exception as e:
            print(e)
            angle = 0
        if angle <= self.viewwidth / 2 or angle >= 2*math.pi - self.viewwidth / 2:
            return True
        else:
            return False

    def calculateUpdate(self, screensize, fishes,  centerForce = 1, velForce = 1, pushAwayStrength = 1, pushAwayDistance = 40, friction = FRICTION):
        # Update velocity when fish meets the border
        vel = self.vel[:]
        if self.pos[0] > screensize[0] - 20:
            vel[0] -= 0.1
        elif self.pos[0] < 20:
            vel[0] += 0.1

        if self.pos[1] > screensize[1] - 20:
            vel[1] -= 0.1
        elif self.pos[1] < 20:
            vel[1] += 0.1
        
        avgPosition = [0, 0]
        avgVel = [0, 0]
        fishesInView = 0
        for fish in fishes:
            if fish == self:
                continue
            if self.isInFov(fish):
                if (distance(fish.pos, self.pos) < pushAwayDistance):
                    strength = (pushAwayDistance-distance(fish.pos, self.pos)) * 0.0001 *pushAwayStrength
                    vel[0] += (self.pos[0] - fish.pos[0]) * strength
                    vel[1] += (self.pos[1] - fish.pos[1]) * strength
                avgPosition = [avgPosition[0] + fish.pos[0], avgPosition[1] + fish.pos[1]]
                avgVel = [avgVel[0] + fish.vel[0], avgVel[1] + fish.vel[1]]
                fishesInView += 1

        if fishesInView != 0:
            avgPosition = [avgPosition[0] / fishesInView, avgPosition[1] / fishesInView]
            avgVel = [avgVel[0] / fishesInView, avgVel[1] / fishesInView]

            vel[0] += avgVel[0] / 150 * velForce
            vel[1] += avgVel[1] / 150 * velForce

            vel[0] += (avgPosition[0] - self.pos[0]) * 0.0006 * centerForce
            vel[1] += (avgPosition[1] - self.pos[1]) * 0.0006 * centerForce

        if vectorLength(vel) < BOOST_THRESHOLD:
            vel = [random.random() * BOOST + vel[0], random.random() * BOOST + vel[1]] 

        if vectorLength(vel) > FRICTION_THRESHOLD:
            vel = [friction * vel[0], friction * vel[1]]
        
        self.nextvel = vel
        self.nextpos = self.pos[0] + self.vel[0], self.pos[1] + self.vel[1]

    def update(self):
        self.pos = self.nextpos
        self.vel = self.nextvel
        self.rot = self.getRot()

class Boid():
    def __init__(self, screensize, size, color = [150, 150, 255], fishsize = FISHSCALING*1, centerForce = FISHSCALING*1, velForce = FISHSCALING*1, pushAwayStrength = FISHSCALING*1, pushAwayDistance = FISHSCALING*40, viewwidth = 1, viewlength = FISHSCALING*300, friction = FRICTION):
        self.fishes = []
        self.screensize = screensize
        self.size = size
        self.color = color
        self.fishsize = FISHSCALING*fishsize
        self.centerForce = centerForce
        self.velForce = velForce
        self.pushAwayStrength = pushAwayStrength
        self.pushAwayDistance = FISHSCALING*pushAwayDistance
        self.viewwidth = viewwidth
        self.viewlength = FISHSCALING*viewlength
        self.friction = friction

        self.createFishes()

    def createFishes(self):
        for i in range(self.size):
            self.fishes.append(Fish(self.screensize, viewwidth=self.viewwidth, viewlength=self.viewlength))
    
    def update(self):
        for fish in self.fishes:
            fish.calculateUpdate(self.screensize, self.fishes, centerForce=self.centerForce, velForce=self.velForce, pushAwayStrength=self.pushAwayStrength, pushAwayDistance=self.pushAwayDistance, friction=self.friction)
        
        for fish in self.fishes:
            fish.update()

    def draw(self, screen):
        for fish in self.fishes:
            fish.draw(screen, fishcolor=self.color, fishsize=self.fishsize)

def updateBoid(boid):
    boid.update()
    return boid

class MainClass():
    def __init__(self):
        pygame.init()
        self.screensize = self.width, self.height = 2080, 1200
        self.screen = pygame.display.set_mode(self.screensize, pygame.RESIZABLE)
        self.uhr = pygame.time.Clock()

        self.boids = []

        self.setup()

    def reset(self):
        self.boids = []
        self.setup()

    def draw(self):
        self.screen.fill([32, 32, 32])
        for boid in self.boids:
            boid.draw(self.screen)
        pygame.display.flip()

    def update(self, pool):
        for boid in self.boids:
            boid.screensize = self.screen.get_size()
        
        self.boids = pool.map(updateBoid, self.boids)

    def setup(self):
        self.boids.append(Boid(self.screen.get_size(), 80, [150, 255, 150], 0.7, velForce=0.2, pushAwayStrength=3, viewwidth=3, centerForce=3))
        self.boids.append(Boid(self.screen.get_size(), 80, [255, 50, 150], velForce=2, pushAwayStrength=0.5, viewwidth=2))
        self.boids.append(Boid(self.screen.get_size(), 80, [255, 150, 255], velForce=1, pushAwayStrength=2, viewwidth=2, centerForce=10, friction=0.92))
        self.boids.append(Boid(self.screen.get_size(), 80))
        self.boids.append(Boid(self.screen.get_size(), 20, [255, 155, 50], 1.6, pushAwayDistance=100, viewlength=500, viewwidth=1.4))

    def main(self, pool):
        active = True
        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.reset()
            
            self.update(pool)
            self.draw()

            self.uhr.tick(30)
            print(self.uhr.get_fps(), end="\r")

if __name__ == "__main__":
    try:
        pool = mp.Pool(4)
        myClass = MainClass()
        myClass.main(pool)
        pygame.quit()
    finally:
        pool.close()
        pool.join()