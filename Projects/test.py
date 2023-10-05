import pygame

pygame.init()

screensize = x, y = 600, 400
screen = pygame.display.set_mode(screensize, pygame.RESIZABLE)

def main():
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False

        screen.fill([255, 255, 255])
        pygame.display.flip()
        
main()
pygame.quit()