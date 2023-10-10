import pygame, random, pickle

screensize = width, height = 600, 600
screen = pygame.display.set_mode(screensize)

pygame.font.init()

data={}
#with open('data.pickle', 'rb') as handle:
#    data = pickle.load(handle)
data["a"] = "b"

def drawText(screen, value, position, size = 25, color = [0, 0, 0]):
        font = pygame.font.SysFont('arial', size)
        text = font.render(str(value), True, color)
        screen.blit(text, position)

def draw(screen):
    screen.fill([255, 255, 255])
    words = data.keys()
    drawText(screen, next(words), (100, 100))
    pygame.display.flip()

def main():
    global active
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False

        draw(screen)

main()
with open('data.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
pygame.quit()