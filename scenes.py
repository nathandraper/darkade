import pygame
import UI
import palette
import sys
import snake
import pong
import random

# snake constants
NORMAL_FPS = 60
FAST_FPS = 70
MEDIUM_FPS = 30
SLOW_FPS = 15


class SceneManager:
    def __init__(self, scene, name, fps):
        self.scenes = {name:scene}
        self.currently_running = name
        self.fps = fps

    def add_scene(self, scene, name):
        self.scenes[name] = scene
    
    def del_scene(self, name):
        self.scenes.pop(name)
    
    def clear_scenes(self):
        self.scenes.clear()

    def change_scene(self, name, obj, data, delete = False, clear = False):
        # TODO: rework this hack
        if data == "slow":
            self.fps = SLOW_FPS
        elif data == "medium":
            self.fps = MEDIUM_FPS
        elif data == "fast":
            self.fps = FAST_FPS
        else:
            self.fps = NORMAL_FPS

        if clear:
            self.clear_scenes()
        elif delete:
            self.scenes.pop(self.currently_running)

        if name not in self.scenes:
            new = obj(data)
            self.add_scene(new, name)
            self.currently_running = name
        else:
            self.currently_running = name

    def draw(self):
        window = pygame.display.get_surface()
        window.fill(palette.BLACK)
        self.scenes[self.currently_running].draw()
        pygame.display.flip()

    def process_frame(self):
        return self.scenes[self.currently_running].process_frame()


class Scene:
    def __init__(self, data):
        self.data = data

        self.objects = {}
    
    def draw(self):
        for obj in self.objects:
            self.objects[obj].draw()

    def process_frame(self):
        for event in pygame.event.get():
            self.check_quit(event)
    
    def check_quit(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


class Menu(Scene):
    def __init__(self, data):
        super().__init__(data)
        self.objects = []
        self.buttons = []
    
    def setup_ui(self):
        pass
    
    def draw(self):
        for obj in self.objects:
            obj.draw()
    
    def process_frame(self):
        for event in pygame.event.get():
            self.check_quit(event)
            
            button = self.check_key(event) or self.check_click(event)
            if button:
                return button.clicked()

    def add_text(self):
        message = UI.Text(self.text, self.text_color)
        self.objects.append((message))
    
    def add_button(self, text, signal, alignment):
        button = UI.Button(None, text, signal)
        button.align(*alignment)
        self.objects.append(button)
        self.buttons.append(button)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            for button in self.buttons:
                if button.rect.collidepoint(pygame.mouse.get_pos()):
                    return button
        
        return None
    
    def check_key(self, event):
        if event.type == pygame.KEYUP:
            for i, button in enumerate(self.buttons):
                if event.key == pygame.K_1 + i:
                    return button
        return None


class MainMenu(Menu):
    def __init__(self, data):
        super().__init__(data)
        self.text = ["DARKADE"]
        self.text_color = palette.GREEN
        self.setup_ui()

    def setup_ui(self):
        self.add_text()
        self.add_button("PyPong", ["pong", PongMain, None], (2, 0, 6, 5))
        self.add_button("Snake", ["snake", SnakeMain, None], (2, 1, 6, 5))


class PongMain(Menu):
    def __init__(self, data):
        super().__init__(data)
        self.text = ["PyPong"]
        self.text_color = palette.GREEN
        
        self.setup_ui()
    
    def setup_ui(self):
        self.add_text()

        self.add_button("play", ["pong_double", PongDouble, None], (2, 0, 6, 5))
        self.add_button("back", ["main_menu", MainMenu, None, True, True], (2, 1, 6, 5))


class PongDouble(Scene):
    def __init__(self, data):
        super().__init__(data)

        self.win_score = 10

        self.setup_game()

    def setup_game(self):
        # get display dimensions
        window = pygame.display.get_surface()
        width = window.get_width()
        height = window.get_height()

        # scores
        self.score_left = 0
        self.score_right = 0
        
        # set controls
        self.l_up = pygame.K_w
        self.l_down = pygame.K_a
        self.r_up = pygame.K_RIGHTBRACKET
        self.r_down = pygame.K_QUOTE

        # make paddles
        x_buffer = 8
        paddle_height = 70
        paddle_width = 10
        self.objects["left"] = pong.Paddle([x_buffer, height // 2], palette.GREEN, paddle_width, 
                                      paddle_height)
        self.objects["right"] = pong.Paddle([width - x_buffer - paddle_width, height // 2], 
                                       palette.GREEN, paddle_width, paddle_height)

        # make ball
        self.objects["ball"] = pong.Ball(palette.RED)

        # score text
        font_size = 40
        y_buffer = 5
        score_left_pos = (x_buffer, y_buffer)
        score_right_pos = (width - font_size * 2, y_buffer)
        self.objects["left_score"] = UI.GameText(str(self.score_left), score_left_pos, 
                                                 palette.GREEN, font_size)
        self.objects["right_score"] = UI.GameText(str(self.score_right), score_right_pos, 
                                                  palette.GREEN, font_size)

        # make lines
        text_buffer = 40
        bottom_buffer = 10
        self.objects["top"] = pong.Wall(bottom_buffer + text_buffer, palette.WHITE)
        self.objects["bottom"] = pong.Wall(height - bottom_buffer , palette.WHITE)

    def process_frame(self):
        ball = self.objects["ball"]
        left = self.objects["left"]
        right = self.objects["right"]
        top = self.objects["top"]
        bottom = self.objects["bottom"]
        left_text = self.objects["left_score"]
        right_text = self.objects["right_score"]

        window_width = pygame.display.get_surface().get_width()

        for event in pygame.event.get():
            self.check_quit(event)
                
        key_list = pygame.key.get_pressed()
        if key_list[self.l_up]:
            left.up()
        elif key_list[self.l_down]:
            left.down()

        if key_list[self.r_up]:
            right.up()
        elif key_list[self.r_down]:
            right.down()
            
        ball.move()
        if ball.x < 0:
            self.score_right += 1
            right_text.text = str(self.score_right)
            ball.reset("left")
            left.reset()
            right.reset()
            
        elif ball.x > window_width:
            self.score_left += 1
            left_text.text = str(self.score_left)
            ball.reset("right")
            left.reset()
            right.reset()
            
        if self.score_left >= self.win_score or self.score_right >= self.win_score:
            return ("pong_end", PongEnd, (self.score_left, self.score_right), True)

        if ball.y < top.y:
            ball.y = top.y + 1
            ball.direction[1] *= -1
            
        elif ball.y > bottom.y:
            ball.y = bottom.y - 1
            ball.direction[1] *= -1

        if ball.rect.colliderect(left.rect):
            ball.redirect(*left.bounce(ball.x, ball.y - ball.height // 2, "left"))

        elif ball.rect.colliderect(right.rect):
            ball.redirect(*right.bounce(ball.x, ball.y - ball.height // 2, "right"))


class PongEnd(Menu):
    def __init__(self, data):
        super().__init__(data)
        self.score_left, self.score_right = self.data

        if self.score_left > self.score_right:
            winner = "left"
        else:
            winner = "right"

        self.text = [f"{winner} side sucked less than the other side", 
                     f"Final score: {self.score_left} - {self.score_right}",
                     "press enter to continue"]
        self.text_color = palette.WHITE

        self.setup_ui()

    def setup_ui(self):
        self.add_text()
    
    def process_frame(self):
        for event in pygame.event.get():
            self.check_quit(event)
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    return ("pong_main", PongMain, None, True)

class SnakeMain(Menu):
    def __init__(self, data):
        super().__init__(data)
        self.text = ["SNAKE"]
        self.text_color = palette.GREEN
        self.setup_ui()
    
    def setup_ui(self):
        self.add_text()
        self.add_button("Slow", ["snake_single", SnakeSingle, "slow"], (3, 0, 6, 4))
        self.add_button("Medium", ["snake_single", SnakeSingle, "medium"], (3, 1, 6, 4))
        self.add_button("Fast", ["snake_single", SnakeSingle, "fast"], (3, 2, 6, 4))
        self.add_button("Back", ["main_menu", MainMenu, None, True, True], (1, 0, 6, 5))


class SnakeSingle(Scene):
    def __init__(self, data):
        super().__init__(data)
        self.block_size = 20
        
        self.setup_game()
    
    def setup_game(self):
        # reset
        window = pygame.display.get_surface()
        window_width = window.get_width()
        window_height = window.get_height()

        self.objects["snake"] = snake.Snake([window_width // 2, window_height // 2], palette.GREEN, 
                                 self.block_size)
        self.objects["food"] = self.spawn_food()
        self.score = 0
    
    def spawn_food(self):
        window = pygame.display.get_surface()
        window_width = window.get_width()
        window_height = window.get_height()

        x = random.randint(1, window_width - self.block_size)
        y = random.randint(1, window_height - self.block_size)

        return snake.Food((x, y), palette.RED, self.block_size)

    def process_frame(self):
        window = pygame.display.get_surface()
        window_width = window.get_width()
        window_height = window.get_height()

        for event in pygame.event.get():
            self.check_quit(event)

        for rect in self.objects["snake"].tail_rects:
            if self.objects["snake"].head_rect.colliderect(rect):
                return self.lose()
        
        x = self.objects["snake"].pos[0]
        y = self.objects["snake"].pos[1]
        if x > window_width or x < 0 or y > window_height or y < 0:
            return self.lose()
        
        if self.objects["snake"].head_rect.colliderect(self.objects["food"].rect):
            grow = True
            self.objects["food"] = self.spawn_food()
            self.score += 1
        else:
            grow = False
            
        key_list = pygame.key.get_pressed()
        if key_list[pygame.K_UP] or key_list[pygame.K_w]:
            if self.objects["snake"].direction != pygame.K_DOWN:
                self.objects["snake"].direction = pygame.K_UP
                
        elif key_list[pygame.K_DOWN] or key_list[pygame.K_s]:
            if self.objects["snake"].direction != pygame.K_UP:
                self.objects["snake"].direction = pygame.K_DOWN
                
        elif key_list[pygame.K_LEFT] or key_list[pygame.K_a]:
            if self.objects["snake"].direction != pygame.K_RIGHT:
                self.objects["snake"].direction = pygame.K_LEFT

        elif key_list[pygame.K_RIGHT] or key_list[pygame.K_d]:
            if self.objects["snake"].direction != pygame.K_LEFT:
                self.objects["snake"].direction = pygame.K_RIGHT

        self.objects["snake"].move(grow)

    def lose(self):
        return ("snake_end", SnakeEnd, self.score, True)


class SnakeEnd(Menu):
    def __init__(self, data):
        super().__init__(data)
        self.text = ["LOSER!", f"Score: {self.data}", "Press ENTER to continue"]
        self.text_color = palette.WHITE

        self.setup_ui()

    def setup_ui(self):
        self.add_text()
    
    def process_frame(self):
        for event in pygame.event.get():
            self.check_quit(event)
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    return ("snake_main", SnakeMain, None, True)
    


