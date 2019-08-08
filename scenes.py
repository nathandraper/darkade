import pygame
import UI
import palette
import sys
import snake
import pong
import random

NORMAL_FPS = 60

class SceneManager:
    def __init__(self, scene, name):
        self.scenes = {name:scene}
        self.currently_running = name
        self.fps = self.scenes[self.currently_running].fps

    def add_scene(self, scene, name):
        self.scenes[name] = scene
    
    def del_scene(self, name):
        self.scenes.pop(name)
    
    def clear_scenes(self):
        self.scenes.clear()

    def change_scene(self, name, obj, data, delete = False, clear = False):
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
        self.fps = self.scenes[self.currently_running].fps
        return self.scenes[self.currently_running].process_frame()


class Scene:
    def __init__(self, data):
        self.data = data

        self.replay_size = 150
        self.fps = NORMAL_FPS
        self.objects = {}
        self.replay = [None] * self.replay_size
        self.replay_pointer = 0

    def replay_snapshot(self):
        window = pygame.display.get_surface()
        width = window.get_width()
        height = window.get_height()

        surface = pygame.surface.Surface((width, height))
        self.draw(surface)
        self.replay[self.replay_pointer] = surface
        
        self.replay_pointer = (self.replay_pointer + 1) % len(self.replay)
    
    def get_replay(self):
        return [self.replay, self.replay_pointer]

    def reset_replay(self):
        self.replay = [None] * 150
        self.replay_pointer = 0

    def surface_snapshot(self):
        window = pygame.display.get_surface()
        width = window.get_width()
        height = window.get_height()

        surface = pygame.surface.Surface((width, height))

        self.draw(surface)
        return surface
    
    def draw(self, surface=None):
        if surface is None:
            surface = pygame.display.get_surface()
        for obj in self.objects.values():
            obj.draw(surface)

    def process_frame(self):
        for event in pygame.event.get():
            self.check_quit(event)
    
    def check_quit(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


class Replay(Scene):
    def __init__(self, data):
        super().__init__(data)
        self.fps = 30
        self.replay, self.last_frame, self.next_scene = self.data
        self.replay_pointer = self.start_frame(self.replay, self.last_frame)
        self.frame = self.replay[self.replay_pointer]
        
        self.flash = (60, 120)
        width = pygame.display.get_surface().get_width()
        self.text = UI.GameText("INSTANT REPLAY", (width // 2, 40), palette.GREEN,
                                40, self.flash)
    
    def process_frame(self):
        for event in pygame.event.get():
            self.check_quit(event)

        if self.frame is None or self.replay_pointer == self.last_frame:
            return self.next_scene

        self.replay_pointer = (self.replay_pointer + 1) % len(self.replay)
        self.frame = self.replay[self.replay_pointer]

    def draw(self):
        if self.frame:
            window = pygame.display.get_surface()
            window.blit(self.frame, (0, 0))
        self.text.draw()
    
    def start_frame(self, replay, pointer):
        start_frame = (pointer + 1) % len(replay)
        
        if replay[start_frame] is None:
            start_frame = 0

        return start_frame


class Countdown(Scene):
    def __init__(self, data):
        super().__init__(data)
        self.background, self.text, self.text_frames, self.next_scene = data
        self.line = 0
        self.frame = 0
        self.lines = self.make_texts()

        self.objects[""] = self.lines[0]

    def make_texts(self):
        lines = []
        for line in self.text:
            text = UI.Text(line, palette.WHITE)
            lines.append(text)
        return lines

    def process_frame(self):
        for event in pygame.event.get():
            self.check_quit(event)
            
        if self.frame >= self.text_frames:
            self.line += 1
            self.frame = 0 

        if self.line >= len(self.lines):
            return self.next_scene
        
        self.frame += 1

    def draw(self):
        window = pygame.display.get_surface()
        window.blit(self.background, (0, 0))
        self.lines[self.line].draw()

    
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

            return self.check_key(event) or self.check_click(event)

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
                    return button.clicked()
        
        return None
    
    def check_key(self, event):
        if event.type == pygame.KEYUP:
            for i, button in enumerate(self.buttons):
                if event.key == pygame.K_1 + i:
                    return button.clicked()
        return None


class MainMenu(Menu):
    def __init__(self, data):
        super().__init__(data)
        self.text = ["DARKADE"]
        self.text_color = palette.GREEN
        self.setup_ui()

    def setup_ui(self):
        self.add_text()
        self.add_button("PyPong", lambda: ["pong", PongMain, None], (2, 0, 6, 5))
        self.add_button("Snake", lambda: ["snake", SnakeMain, None], (2, 1, 6, 5))


class PongMain(Menu):
    def __init__(self, data):
        super().__init__(data)
        self.text = ["PyPong"]
        self.text_color = palette.GREEN
        
        self.setup_ui()
    
    def setup_ui(self):
        self.add_text()

        self.add_button("play", lambda: ["pong_double", PongDouble, None], (2, 0, 6, 5))
        self.add_button("back", lambda: ["main_menu", MainMenu, None, True, True], (2, 1, 6, 5))


class PongDouble(Scene):
    def __init__(self, data):
        super().__init__(data)

        self.win_score = 10
        self.countdown = True

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
        if self.countdown:
            self.countdown = False
            return self.end_round()

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
        if ball.x < 0 or ball.x > window_width:
            return self.end_round()

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
    
    def end_round(self):
        if self.objects["ball"].x < 0:
            self.score_right += 1
            self.objects["ball"].reset("left")
            self.objects["right_score"].text = str(self.score_right)

        else:
            self.score_left += 1
            self.objects["ball"].reset("right")
            self.objects["left_score"].text = str(self.score_left)
        
        if self.score_left >= self.win_score or self.score_right >= self.win_score:
            return ("pong_end", PongEnd, (self.score_left, self.score_right), True)

        self.objects["left"].reset()
        self.objects["right"].reset()

        back = ("pong_double", PongDouble, self.data, True)
        countdown = ("countdown", Countdown, 
                     (self.surface_snapshot(), [["Ready..."], ["Go!"]], 30, back))
                     
        return countdown


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
        self.add_button("Slow", self.speed_signal(20, 0), (3, 0, 6, 4))
        self.add_button("Medium", self.speed_signal(40, 1), (3, 1, 6, 4))
        self.add_button("Fast", self.speed_signal(70, 2), (3, 2, 6, 4))
        self.add_button("1p", self.start_game_signal("1p"), (3, 0, 6, 5))
        self.add_button("2p", self.start_game_signal("2p"), (3, 1, 6, 5))
        self.add_button("Back", lambda: ["main_menu", MainMenu, None, True, True], (3, 2, 6, 5))
        
        self.buttons[1].clicked()

    def speed_signal(self, fps, num):
        def signal():
            self.fps = fps
            self.buttons[num].button_color = palette.GREEN
            whites = [0, 1, 2]
            whites.remove(num)
            for white in whites:
                self.buttons[white].button_color = palette.WHITE

        return signal
    
    def start_game_signal(self, mode):
        if mode == "1p":
            name = "snake_single"
            game = SnakeSingle
        elif mode == "2p":
            name = "snake_double"
            game = SnakeDouble

        def signal():
            return (name, game, self.fps)

        return signal
        

class SnakeSingle(Scene):
    def __init__(self, data):
        super().__init__(data)
        self.fps = self.data
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


class SnakeDouble(Scene):
    def __init__(self, data):
        super().__init__(data)
        self.fps = self.data
        self.block_size = 20

        self.countdown = True
        self.countdown_text = [["Ready"], ["Go!"]]
        self.countdown_length = 120

        self.setup_game()
    
    def setup_game(self):
        window = pygame.display.get_surface()
        window_width = window.get_width()
        window_height = window.get_height()

        buffer = 5 * self.block_size
        self.p1_starting_pos = (buffer, buffer)
        self.p2_starting_pos = (window_width - buffer, window_height - buffer)

        self.objects["p1"] = snake.Snake(self.p1_starting_pos, palette.GREEN, self.block_size)
        self.objects["p2"] = snake.Snake(self.p2_starting_pos, palette.BLUE, self.block_size)
        self.objects["food"] = self.spawn_food()

        self.objects["p1"].direction = pygame.K_DOWN
        self.objects["p2"].direction = pygame.K_UP

        self.p1_controls = [pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a]
        self.p2_controls = [pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]

        self.p1_score = 0
        self.p2_score = 0

    def process_frame(self):
        self.replay_snapshot()

        if self.p1_score >= 3 or self.p2_score >= 3:
            return self.match()

        if self.countdown:
            back = ("snake_double", SnakeDouble, self.data, True)
            self.countdown = False
            return ("countdown", Countdown, (self.surface_snapshot(), self.countdown_text, 
                    self.countdown_length, back))
            
        window = pygame.display.get_surface()
        window_width = window.get_width()
        window_height = window.get_height()

        p1 = self.objects["p1"]
        p2 = self.objects["p2"]
        food = self.objects["food"]

        for event in pygame.event.get():
            self.check_quit(event)
        
        snakes = [p1, p2]
        controls = [self.p1_controls, self.p2_controls]
        key_list = pygame.key.get_pressed()
        for i, (snake, controls) in enumerate(zip(snakes, controls)):
            other_snake = not i
            for rect in snake.tail_rects:
                if snakes[other_snake].head_rect.colliderect(rect):
                    return self.win(i)

            x = snake.pos[0]
            y = snake.pos[1]
            if x > window_width or x < 0 or y > window_height or y < 0:
                return self.win(other_snake)
            
            if snake.head_rect.colliderect(food.rect):
                grow = True
                self.objects["food"] = self.spawn_food()
            else:
                grow = False
        
            if key_list[controls[0]]:
                if snake.direction != pygame.K_DOWN:
                    snake.direction = pygame.K_UP

            elif key_list[controls[1]]:
                if snake.direction != pygame.K_LEFT:
                    snake.direction = pygame.K_RIGHT

            elif key_list[controls[2]]:
                if snake.direction != pygame.K_UP:
                    snake.direction = pygame.K_DOWN
                    
            elif key_list[controls[3]]:
                if snake.direction != pygame.K_RIGHT:
                    snake.direction = pygame.K_LEFT

            snake.move(grow)

    def spawn_food(self):
        window = pygame.display.get_surface()
        window_width = window.get_width()
        window_height = window.get_height()

        x = random.randint(1, window_width - self.block_size)
        y = random.randint(1, window_height - self.block_size)

        return snake.Food((x, y), palette.RED, self.block_size)
    
    def win(self, winner):
        if winner:
            winner = "blue"
            self.p2_score += 1
        else:
            winner = "green"
            self.p1_score += 1

        back = ("snake_double", SnakeDouble, self.data, True)
        replay = ("replay", Replay, self.get_replay() + [back], True)
        countdown = ("countdown", Countdown, 
                     (self.surface_snapshot(), [[f"{winner} wins!"]], 90, replay))
                     
        
        self.countdown = True
        self.objects["p1"].reset(self.p1_starting_pos, pygame.K_DOWN)
        self.objects["p2"].reset(self.p2_starting_pos, pygame.K_UP)
        self.objects["food"] = self.spawn_food()
        
        self.reset_replay()
        
        return countdown

    def match(self):
        window = pygame.display.get_surface()
        width = window.get_width()
        height = window.get_height()

        if self.p1_score > self.p2_score:
            winner = "green"
        else:
            winner = "blue"
        
        surface = pygame.surface.Surface((width, height))
        surface.fill(palette.BLACK)
        
        line1 = [f"{winner} wins the set!"]
        line2 = ["Final Score:", f"green {self.p1_score} - {self.p2_score} blue"]

        back = ("snake_main", SnakeMain, None, True)
        countdown = ("countdown", Countdown, (surface, [line1, line2], 120, back), True)

        return countdown
        

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
    


