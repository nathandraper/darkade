import pygame
import os
import scenes
import random

FPS = 60

random.seed()

# set game window location
win_x = 30
win_y = 50
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{win_x},{win_y}"

# init display
window_width = 1300
window_height = 800

pygame.init()
pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Darkade")

clock = pygame.time.Clock()
main_menu = scenes.MainMenu(None)
program = scenes.SceneManager(main_menu, "main_menu", FPS)

while True:
    result = program.process_frame()
    if result:
        program.change_scene(*result)

    program.draw()
    clock.tick(program.fps)


