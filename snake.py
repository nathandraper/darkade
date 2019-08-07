import pygame

class Snake:
    def __init__(self, pos, color, block_size):
        self.pos = pos
        self.color = color
        self.block_size = block_size

        self.head_rect = pygame.Rect(pos[0], pos[1],
            self.block_size, self.block_size)

        self.tail_rects = []
        self.direction = None
        
    def move(self, grow):

        if self.direction == pygame.K_UP:
            self.pos[1] -= self.block_size

        elif self.direction == pygame.K_DOWN:
            self.pos[1] += self.block_size
        
        elif self.direction == pygame.K_LEFT:
            self.pos[0] -= self.block_size
        
        elif self.direction == pygame.K_RIGHT:
            self.pos[0] += self.block_size
        
        if self.direction is not None:
            self.tail_rects.append(self.head_rect)
            if not grow:
                self.tail_rects.pop(0)
            self.head_rect = pygame.Rect(self.pos[0], self.pos[1], self.block_size, self.block_size)

    def draw(self):
        window = pygame.display.get_surface()
        
        pygame.draw.rect(window, self.color, self.head_rect)
        for rect in self.tail_rects:
            pygame.draw.rect(window, self.color, rect)

class Food:
    def __init__(self, pos, color, block_size):
        self.pos = pos
        self.color = color
        self.block_size = block_size

        self.rect = pygame.rect.Rect(pos[0], pos[1], self.block_size, self.block_size) 
    
    def draw(self):
        window = pygame.display.get_surface()
        pygame.draw.rect(window, self.color, self.rect)
    