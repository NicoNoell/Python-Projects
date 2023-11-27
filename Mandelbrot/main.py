import pygame

pygame.init()

screensize = width, height = 600, 600
screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)
uhr = pygame.time.Clock()

minX, maxX = -2.2, 0.8
minY, maxY = -1.5, 1.5
maxIter = 20

def calculatePoint(constant_real, constant_imaginary):
    counter = 0
    real, imaginary = 0, 0
    while (abs(real) + abs(imaginary)) < 50 and counter < maxIter:
        newReal = real**2 - imaginary**2 + constant_real
        imaginary = 2*real*imaginary + constant_imaginary
        real = newReal
        counter += 1
    return 1-(counter/maxIter)

def draw(screen):
    screen.fill([255, 255, 255])
    for y in range(height):
        for x in range(width):
            value = calculatePoint(x/width * (maxX-minX) + minX, y/height * (maxY-minY) + minY)
            color = [value*255, value*255, value*255]
            pygame.draw.rect(screen, color, [x, y, 1, 1])
    pygame.display.flip()

def main():
    draw(screen)
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False

        uhr.tick(30)
        
main()
pygame.quit() 