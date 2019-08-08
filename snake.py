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
            x = self.pos[0]
            y = self.pos[1] - self.block_size
            self.pos = (x, y)

        elif self.direction == pygame.K_DOWN:
            x = self.pos[0]
            y = self.pos[1] + self.block_size
            self.pos = (x, y)
        
        elif self.direction == pygame.K_LEFT:
            x = self.pos[0] - self.block_size
            y = self.pos[1]
            self.pos = (x, y)
        
        elif self.direction == pygame.K_RIGHT:
            x = self.pos[0] + self.block_size
            y = self.pos[1]
            self.pos = (x, y)
        
        if self.direction is not None:
            self.tail_rects.append(self.head_rect)
            if not grow:
                self.tail_rects.pop(0)
            self.head_rect = pygame.Rect(self.pos[0], self.pos[1], self.block_size, self.block_size)

    def draw(self, surface=None):
        if surface is None:
            window = pygame.display.get_surface()
        else:
            window = surface
        
        pygame.draw.rect(window, self.color, self.head_rect)
        for rect in self.tail_rects:
            pygame.draw.rect(window, self.color, rect)
    
    def reset(self, pos, direction):
        self.pos = pos
        self.direction = direction
        self.tail_rects = []
        self.head_rect = pygame.rect.Rect(self.pos[0], self.pos[1], 
                                          self.block_size, self.block_size)

class Food:
    def __init__(self, pos, color, block_size):
        self.pos = pos
        self.color = color
        self.block_size = block_size

        self.rect = pygame.rect.Rect(pos[0], pos[1], self.block_size, self.block_size) 
    
    def draw(self, surface=None):
        if surface is None:
            window = pygame.display.get_surface()
        else:
            window = surface
        pygame.draw.rect(window, self.color, self.rect)
    