import math
import pygame
import random

class Ball:
    def __init__(self, color):
        self.color = color
        
        self.speed = 15
        self.width = 10
        self.height = 10

        self.direction = [None, None]

        self.reset(None)        
    
    def reset(self, serve):
        window = pygame.display.get_surface()
        window_width = window.get_width()
        window_height = window.get_height()
        self.x = window_width // 2 - self.width // 2
        self.y = window_height // 2 - self.height // 2

        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
        
        if serve is None:
            serve = random.choice(["left", "right"])
        
        if serve == "left":
            self.direction[0] = -self.speed

        else:
            self.direction[0] = self.speed

        self.direction[1] = 0
    
    def move(self):
        self.x += self.direction[0]
        self.y += self.direction[1]
        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)

    def redirect(self, new_x, angle):
        self.x = new_x
        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)

        x_vel = self.speed * math.cos(angle)
        y_vel = self.speed * math.sin(angle)
        self.direction = [x_vel, y_vel]
    
    def draw(self):
        window = pygame.display.get_surface()
        pos = (round(self.x), round(self.y))
        pygame.draw.circle(window, self.color, pos, self.width // 2)
    

class Paddle:
    def __init__(self, pos, color, width, height):
        self.pos = pos
        self.color = color
        self.speed = 10

        self.height = height
        self.width = width

        self.reset()
        
    def reset(self):
        window_height = pygame.display.get_surface().get_height()
        self.pos[1] = window_height // 2 - self.height // 2
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], self.width, self.height) 

    def up(self):
        self.pos[1] -= self.speed
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], self.width, self.height) 

    def down(self):
        self.pos[1] += self.speed
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], self.width, self.height) 

    def bounce(self, ball_x, ball_y, side):
        max_angle = 1.2
        center = self.height // 2
        dist = ball_y - self.pos[1]
        angle = max_angle * ((dist - center) / center)
        
        # hack to fix a bug
        if angle > max_angle or angle < -max_angle:
            angle = math.copysign(max_angle, angle)
        
        if side == "left":
            new_x = self.pos[0] + self.width + 1

        elif side == "right":
            new_x = self.pos[0] - self.width + 1
            angle = math.pi - angle


        return new_x, angle
    
    def draw(self):
        window = pygame.display.get_surface()
        pygame.draw.rect(window, self.color, self.rect)

class Wall:
    def __init__(self, y, color):
        self.y = y
        self.color = color
        self.rect = pygame.rect.Rect(0, y, pygame.display.get_surface().get_width(), 5)
    
    def draw(self):
        pygame.draw.rect(pygame.display.get_surface(), self.color, self.rect)