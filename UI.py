import pygame
import palette

# UI constants
TEXT_SIZE = 90
TEXT_BUFFER = 10
BUTTON_TEXT_SIZE = 70

BUTTON_BUFFER_X = 15
BUTTON_BUFFER_Y = 10
BUTTON_LINE_WIDTH = 5

BUTTON_COLOR = palette.WHITE
TEXT_COLOR = palette.GREEN


class Button:
    def __init__(self, pos, text, signal, x_buffer = BUTTON_BUFFER_X, 
                 y_buffer = BUTTON_BUFFER_Y, line_width = BUTTON_LINE_WIDTH,
                 font_size = BUTTON_TEXT_SIZE, button_color = BUTTON_COLOR,
                 TEXT_COLOR = TEXT_COLOR):

        self.text = text
        self.signal = signal

        self.line_width = line_width
        self.x_buffer = x_buffer
        self.y_buffer = y_buffer
        self.font_size = font_size
        self.text_color = TEXT_COLOR
        self.button_color = button_color

        self.font = pygame.font.Font(None, self.font_size)
        self.text_size = self.font.size(self.text)
        self.message = self.font.render(self.text, True, self.text_color)

        self.width = self.text_size[0] + self.x_buffer
        self.height = self.text_size[1] + self.y_buffer
        
        if pos is not None:
            self.pos = (pos[0] - self.width // 2, pos[1] - self.height // 2)
            self.update_rect()
    
    def draw(self):
        window = pygame.display.get_surface()
        text_pos = (self.pos[0] + self.x_buffer // 2, self.pos[1] + self.y_buffer // 2)
        window.blit(self.message, (text_pos))
        pygame.draw.rect(window, self.button_color, self.rect, self.line_width)

    def clicked(self):
        return self.signal
    
    def align(self, x_divs, x, y_divs, y):
        window = pygame.display.get_surface()
        width = window.get_width()
        height = window.get_height()

        x_pos = (width / x_divs) * x + (width / x_divs) // 2 - self.width // 2
        y_pos = (height / y_divs) * y + (height / y_divs) // 2 - self.height // 2

        self.pos = (x_pos, y_pos)
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], self.width, self.height)

class Text():
    def __init__(self, lines, color):
        self.surface = pygame.display.get_surface()
        self.lines = lines
        self.color = color

    def draw(self):
        font = pygame.font.Font(None, TEXT_SIZE)
        screen_width = self.surface.get_width()
        screen_height = self.surface.get_height()
        sizes = []
        messages = []
        text_height = 0
        
        for line in self.lines:
            size = font.size(line)
            sizes.append(size)
            text_height += size[1]
            messages.append(font.render(line, True, self.color))
        
        text_height += TEXT_BUFFER * (len(self.lines) - 1)
        
        y = screen_height // 2 - text_height // 2
        for size, message in zip(sizes, messages):
            x = screen_width // 2 - size[0] // 2
            self.surface.blit(message, (x, y))
            y += size[1] + TEXT_BUFFER

class GameText:
    def __init__(self, text, pos, color, font_size):
        self.text = text
        self.pos = pos
        self.color = color
        self.font_size = font_size
        self.font = pygame.font.Font(None, self.font_size)

    def draw(self):
        window = pygame.display.get_surface()
        message = self.font.render(self.text, True, self.color)
        window.blit(message, self.pos)
        