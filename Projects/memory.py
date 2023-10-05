import pygame, random

screensize = width, height = 600, 600
screen = pygame.display.set_mode(screensize)

class Card:
    def __init__(self, x, y, size, number) -> None:
        """x, y and z are given in Pixels"""
        self.x = x
        self.y = y
        self.size = size
        self.number = number
        self.isRevealed = False

        self.border = int(self.size / 18)
        self.color = [(self.number * 83 + 40) % 256, (self.number * 27 + 80) % 256, (self.number * 175 + 170) % 256]
        self.rect = pygame.Rect(self.x + self.border, self.y + self.border, self.size - 2*self.border, self.size - 2*self.border)

    def draw(self, screen):
        pygame.draw.rect(screen, [20, 20, 20], [self.x, self.y, self.size, self.size])
        if self.isRevealed:
            pygame.draw.rect(screen, self.color, self.rect, 0, 3*self.border)
        else:
            pygame.draw.rect(screen, [170, 170, 170], self.rect, 0, 3*self.border)

    def isHitBy(self, pos):
        return pygame.Rect.collidepoint(self.rect, pos[0], pos[1])


class Field:
    def __init__(self, size) -> None:
        self.size = size
        self.sizePerCard = (width/self.size)
        self.field = []
        self.createField()
        self.firstCard = 0
    
    def createField(self):
        numbers = []
        for i in range(0, self.size**2, 1):
            numbers.append(int(i/2))
        
        random.shuffle(numbers)

        for x in range(self.size):
            for y in range(self.size):
                self.field.append(Card(self.sizePerCard*x, self.sizePerCard*y, self.sizePerCard, numbers[-1]))
                numbers.pop()

    def draw(self, screen):
        for card in self.field:
            card.draw(screen)

    def flipCard(self, pos):
        global active
        for card in self.field:
            if card.isHitBy(pos):
                if card.isRevealed:
                    return

                card.isRevealed = True
                print("Card revealed")
                if self.firstCard == 0:
                    self.firstCard = card

                elif self.firstCard.number != card.number:
                    i = 20
                    while i > 0:
                        for event in pygame.event.get():
                            if event == pygame.QUIT:
                                active = False
                                return
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                i = 0
                        card.draw(screen)
                        pygame.display.flip()
                        pygame.time.wait(100)
                        i -= 1
                        
                    card.isRevealed = False
                    self.firstCard.isRevealed = False
                    self.firstCard = 0
                else:
                    self.firstCard = 0
                return


def draw(screen):
    screen.fill([255, 255, 255])
    myField.draw(screen)
    pygame.display.flip()

def main():
    global active
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                myField.flipCard(event.pos) 

        draw(screen)

myField = Field(6)
main()
pygame.quit()