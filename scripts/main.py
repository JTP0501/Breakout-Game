import pyxel
import json
from dataclasses import dataclass
from enum import Enum, auto
from math import radians, sin, cos
from random import choice

from reward import Reward
from ball import Ball
from paddle import Paddle 
from brick import Brick
from sounds import Sounds


class GameState(Enum):
    """ Game states enumeration """
    START = auto() # starting screen
    READY = auto() # ready to start 
    RUNNING = auto() # in progress
    DROPPED = auto() # ball is out of bounds
    STAGE_TRANSITION = auto() # transitioning state
    GAME_OVER = auto() # player lost the game
    WIN = auto() # player won the game

@dataclass
class GameStats:
    score: int = 0 # score tracker
    lives: int = 3 # lives tracker

class BreakoutGame:

    def __init__(self) -> None:
        """ Constructor """
        self._init_pyxel() # initializes pyxel settings
        self.gravity: float = 0.010
        self.paddle: Paddle = Paddle() # initializes a paddle
        self.original_paddle_speed: float = self.paddle.speed
        # relates to the indicator when game starts
        self.angle: float # angle tracker for indicator
        self.angle_direction: float # 1 is left to right, -1 is right to left
        self.angle_cycle_speed: float # degrees per frame     

        self.ball: Ball = Ball(self.gravity) # initializes a ball
        self.balls: list[Ball] = [self.ball] # initially put og ball inside list of balls
        self._reset_ball() # makes sure that ball starts at paddle 

        self.P, self.g, self.X, self.Q, self.stages = self._load_stages("../assets/stages.json") # contains all the predefined stages
        self.G = self.g * 60 # redefines G (60 fps)
        self.current_stage: int # tracks the current stage no. 
        
        self.bricks: list[Brick] = [] # tracks the list of bricks imported from the current stage
        self.score_objects: list[Reward] = [] # tracks the list of score objects currently at play

        self.current_game_state: GameState # game state tracker
        self.sound: Sounds = Sounds() # sound player
        self.dropped_timer: float = 0  # timer for DROPPED state
        self.transition_timer: float = 0 # time for STAGE_TRANSITION state
        self._start_new_game() # starts a new game
        
        # dropped state prompts
        self.calcifer_sprites: list[tuple[int, int]] = [(48,64), (88, 64)]
        self.chosen_skin: tuple[int, int] # tracks calcifer sprite
        self.dropped_msgs: list[str] = ["Don't do that again, unless you want to feel my wrath. (T-T)",
                                        "I am an extremely powerful fire demon, I won't let you humiliate me.",
                                        "Please, don't drop me again.",
                                        "What are you doing?!?!?",
                                        ]
        self.chosen_msg: str
        pyxel.run(self._update, self._draw) # runs game loop
  
    @classmethod
    def _init_pyxel(cls) -> None:
        """ Initializes Pyxel engine settings """
        pyxel.init(width=450, height=200, display_scale=3, title="Breakout Game", fps=60)
        pyxel.load("../assets/resources.pyxres") # our resource file

    # +++++++++++++++++++++++++++++++++ STAGE MANAGEMENT +++++++++++++++++++++++++++++++++

    @classmethod
    def _load_stages(cls, file_path: str) -> tuple[int, int, int, int, list[dict[str, list[dict[str, int]]]]]:
        """ Load stages from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return data["P"], data["G"], data["X"], data["Q"], data["stages"]

    def _load_stage(self, stage_index: int) -> None:
        """ Load a specific stage."""
        stage = self.stages[stage_index] # stages is 0-indexed
        self.bricks = [
            # we want to randomize the no. of score objects that spawn from a brick (will deal with the objects colliding soon)
            Brick(brick["x"], brick["y"], brick["brick_type"], K=pyxel.rndi(2,4)) # random K from 2 to 4
            for brick in stage["bricks"]
        ]

    def _next_stage(self) -> None:
        """ Move to the next stage."""
        if self.current_stage < len(self.stages):
            self.current_stage += 1
            self.transition_timer = pyxel.frame_count  # initializes the transition timer (snapshot of frame count)
            self.current_game_state = GameState.STAGE_TRANSITION
        else:
            self.current_game_state = GameState.WIN

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++

    def _start_new_game(self) -> None:
        """ Starts a new game """
        pyxel.stop(ch=1) # mutes channel 1 sounds that were still playing (sound fx)
        self.stats = GameStats() # initializes a GameStats object for new game
        self.paddle.speed = self.original_paddle_speed # resets paddle speed
        self.score_objects.clear() # resets score objects tracker
        self.bricks.clear() # resets old bricks (if there are any)
        self.current_stage = 1 # sets the current stage to the first one (1-indexed)
        self.transition_timer = 0  # resets the stage transition timer
        self._load_stage(self.current_stage - 1) # loads the current stage
        self._reset_ball() # resets ball position to paddle
        self.current_game_state = GameState.START # sets the gamestate to the START state
        self.sound.game_over_played = False # resets game over sound
        self.sound.win_played = False # resets win sound
        pyxel.mouse(True) # enables mouse cursor view
        pyxel.playm(0, loop=True) # plays bgm at start
        
    def _reset_ball(self):
        """ Resets the ball to paddle """
        while len(self.balls) > 1:
            self.balls.pop() # leaves a single ball
        self.ball = self.balls[0] # the remaining ball
        self.ball.clear_trails() # removes trails that could still be up
        self.ball.x = self.paddle.x + self.paddle.w / 2 - self.ball.r  # centers on paddle
        self.ball.y = self.paddle.y - self.ball.r * 2    # keeps the ball above the paddle
        self.angle = 0 # indicator starts with 0 deg
        self.angle_direction = 1 # start going left to right
        self.angle_cycle_speed = 2 # 2 degrees per frame
        # ball is not launched yet
        self.ball.speed_x = 0 
        self.ball.speed_y = 0
        # resets ball's out of bounds state
        self.ball.out_of_bounds = False

    def _launch_ball(self):
        """ Launches the ball based on the current angle """
        angle_rad: float = radians(self.angle)
        self.ball.speed_x = cos(angle_rad) * 2.5
        self.ball.speed_y = -sin(angle_rad) * 2.5

        # transitions to running state
        self.current_game_state = GameState.RUNNING

    def _check_collision(self) -> None:
        """ Checks for all kinds of collisions """
        # Ball vs Paddle
        for ball in self.balls: # loop through all balls in stage currently
            paddle_collision = ball.detect_collision(self.paddle)
            if paddle_collision:
                self.sound.play_ball_hit_sound()

            # Ball vs Bricks
            for i in reversed(range(len(self.bricks))): # checks all bricks for collisions
                b: Brick = self.bricks[i]

                brick_collision = ball.detect_collision(b)
                if brick_collision:
                    self.sound.play_ball_hit_sound()
                    
                    if ball.destroy_brick:
                        if b.brick_type == 5: # if it is a ball maker
                            # makes a new ball and give it a random angle and initial speed
                            new_ball = Ball(self.gravity)  
                            angle = radians(pyxel.rndi(0, 360))  # random angle between 0 and 360 degrees, then converted to radians
                            speed = pyxel.rndf(1,new_ball.MAX_SPEED)  # random speed between 1 and (max_speed)

                            # sets speed in the x and y direction
                            new_ball.speed_x = speed * cos(angle)
                            new_ball.speed_y = -speed * sin(angle)

                            # positions ball at the center of brick
                            new_ball.x = b.x + (b.w / 2)  
                            new_ball.y = b.y + (b.h / 2)

                            self.balls.append(new_ball)  # adds new ball to the game
                            # added ball doesn't carry over to the next stages or if goes into dropped state
                        else:
                            # if not a ball maker, spawns K score objects
                            self._spawn_score_objects(b.K, b)
                        del self.bricks[i] # removes brick that collides with ball and has no health
                        self.ball.destroy_brick = False # resets it
                    break
    
        # Reward vs World (Paddle and Bottom)
        for i in reversed(range(len(self.score_objects))):
            r = self.score_objects[i]
            collision_type, points = r.collides(self.paddle)
            if collision_type is not None: # if it collides
                if collision_type == "paddle":
                    self.sound.play_reward_sound()
                    if r.powerup_type: # if it is a powerup
                        self._apply_powerup(r.powerup_type)
                    if hasattr(self, "double_points") and self.double_points:
                        self.stats.score += (2 * points) # doubles the points of objects collided with
                    else:
                        self.stats.score += points 
                del self.score_objects[i]
    
    def _check_input(self) -> None:
        """ Checks for inputs by user (depending on the game state)"""
        if self.current_game_state == GameState.READY:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE): # press left mouse click or space bar to launch ball
                self.sound.play_launch_sound()
                self._launch_ball() # launches the ball
    
        if self.current_game_state in {GameState.GAME_OVER, GameState.WIN}:
            if pyxel.btnp(pyxel.KEY_RETURN): # press enter to start a new game
                self._start_new_game()
                pyxel.playm(0, loop=True)  # restarts background music

    def _spawn_score_objects(self, K: int, brick: Brick) -> None:
        """ Spawns K rectangular score objects within the bounds of a hit brick """
        
        # brick properties
        brick_x, brick_y = brick.x, brick.y  # top-left corner of the brick

        # score object properties
        obj_width = 8  # fixed width
        obj_height = 10  # fixed height
        padding = 2 # space between objects

        # defines positions for up to 4 objects (manual layout)
        positions = [
        (brick_x + padding, brick_y + padding),  # 1st
        (brick_x + obj_width + padding, brick_y + padding),  # 2nd
        (brick_x + padding, brick_y + 2 * obj_height + padding),  # 3rd
        (brick_x + obj_width + padding, brick_y + 2 * obj_height + padding)  # 4th
        ]

        # spawns K objects
        for i in range(K):
            spawn_x, spawn_y = positions[i]  # uses predefined positions directly

            # appends reward object  
            self.score_objects.append(
                Reward(
                    x=spawn_x,
                    y=spawn_y,
                    points=self.P,
                    falling_accel=self.gravity,
                    X=self.X
                )
            )
        
    def _apply_powerup(self, powerup_type: str) -> None:
        """ Applies the effect of a power-up based on its type """
        if powerup_type == "life_up":
            self.stats.lives += 1 # (carries over)
        elif powerup_type == "antigravity": # has duration G (doesn't carry over)
            self.ball.gravity = 0  # disables gravity 
            if hasattr(self, "antigravity_timer"):
                self.antigravity_timer += self.G  # extends timer (if timer is already there)
            else:
                self.antigravity_timer = self.G  # starts timer
        elif powerup_type == "paddle_speed":
            self.paddle.speed += 0.20 # increase paddle speed by 0.20  (carries over)
        elif powerup_type == "double_points": # has duration G (doesn't carry over)
            self.double_points = True  # activates double points
            if hasattr(self, "double_points_timer"):
                self.double_points_timer += self.G  # extends timer (if timer is already there)
            else:
                self.double_points_timer = self.G  # starts timer

# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def _update_start_state(self) -> None:
        """ Update logic for START state """
        # transitions to READY state when the player presses the Play button
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):  # Mouse click to start
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y

            # checks if the mouse is within the Play button areas
            button_x, button_y = pyxel.width // 2 - 30, pyxel.height // 2 + 50
            button_width, button_height = 60, 15

            if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                pyxel.mouse(False) # disable mouse cursor view
                self.transition_timer = pyxel.frame_count # snapshot of curr frame count
                self.current_game_state = GameState.STAGE_TRANSITION
                self.sound.play_clicked_button_sound()
                
    def _update_ready_state(self) -> None:
        """ Update logic for READY state """
        self.ball.x = self.paddle.x + self.paddle.w / 2 - self.ball.r # centers the ball at the paddle's horizontal center

        # oscillates the angle left to right, then right to left
        self.angle += self.angle_direction * self.angle_cycle_speed

        # reverses direction at bounds
        if self.angle == 180 or self.angle == 0:
            self.angle_direction = -self.angle_direction # reversed direction
    
    def _update_running_state(self) -> None:
        """ Update logic for RUNNING state """

        self._update_timers()

        for ball in self.balls:
            ball.update() # moves the ball
        
        for r in self.score_objects: # moves the score objects
            r.update()

        self._check_collision() # checks for collisions
        # 4 is indestructible
        if not self.bricks or all(brick.brick_type == 4 for brick in self.bricks): # all bricks cleared (stage cleared)
            if not self.score_objects: # if there are not score objects in the screen
                # at end of stage
                if hasattr(self, "antigravity_timer"):
                    self._disable_antigravity()
                if hasattr(self, "double_points"):
                    self._disable_double_points()
                if self.current_stage == len(self.stages): # last stage cleared
                    self.current_game_state = GameState.WIN
                    pyxel.stop()  # stops background music
                else:
                    self._next_stage()

        # removes all balls that are out of bounds
        if len(self.balls) > 1: # if there is still more than 1 ball
            self.balls = [ball for ball in self.balls if not ball.out_of_bounds]

        # checks if all balls are out of bounds
        if len(self.balls) == 1:  # if there is only one ball left
            if self.balls[0].out_of_bounds: # if that singular ball is out of bounds
                self.chosen_skin = choice(self.calcifer_sprites)  # choose a sprite for the dropped screen
                self.chosen_msg = choice(self.dropped_msgs)  # choose a msg for the dropped screen
                self.stats.lives -= 1
                if self.stats.lives > 0:
                    self.current_game_state = GameState.DROPPED
                else:
                    self.current_game_state = GameState.GAME_OVER
                    pyxel.stop()  # stops background music
                 
    def _update_dropped_state(self) -> None:
        """ Updates logic for DROPPED state """
        
        # shows DROPPED screen and resets the ball after a delay
        if self.dropped_timer == 0:
            self.dropped_timer = pyxel.frame_count  # initializes the timer

        # waits for 120 frames (2 seconds at 60 FPS)
        if pyxel.frame_count - self.dropped_timer > 120:
            self.dropped_timer = 0  # resets the timer
            self._reset_ball()  # resets the ball position
            self.current_game_state = GameState.READY

    def _update_stage_transition_state(self) -> None:
        """ Update logic for STAGE_TRANSITION state """
        # waits for 120 frames (2 seconds at 60 FPS)
        if pyxel.frame_count - self.transition_timer > 120:
            self._load_stage(self.current_stage - 1)  # loads the next stage
            self._reset_ball()  # resets the ball to the paddle
            self.current_game_state = GameState.READY
    
    def _update_timers(self) -> None:
        """ Update timers based on game state """
        if self.current_game_state == GameState.RUNNING:
            if hasattr(self, "double_points_timer"):
                self.double_points_timer -= 1  # decrements timer in RUNNING state
            if hasattr(self, "antigravity_timer"):
                self.antigravity_timer -= 1  # decrements timer in RUNNING state
    
    def _disable_double_points(self) -> None:
        """ Disables double points power up"""
        self.double_points = False  # deactivates double points
        if hasattr(self, "double_points_timer"):
            del self.double_points_timer  # removes the timer
    
    def _disable_antigravity(self) -> None:
        """ Disables antigravity power up """
        self.ball.gravity = self.gravity  # restores gravity
        if hasattr(self, "antigravity_timer"):
            del self.antigravity_timer  # removes the timer

    def _update(self) -> None:
        """ General update method """
        self._check_input()
        self.paddle.update()

        match self.current_game_state:
            case GameState.START:
                self._update_start_state()
            case GameState.READY:
                self._update_ready_state()
            case GameState.RUNNING:
                self._update_running_state()
            case GameState.DROPPED:
                self._update_dropped_state()
            case GameState.STAGE_TRANSITION:
                self._update_stage_transition_state()
            case GameState.GAME_OVER:
                self.sound.play_game_over_sound()
            case GameState.WIN:
                self.sound.play_win_sound()

# +++++++++++++++++++++++++++++++++ DRAW METHODS +++++++++++++++++++++++++++++++++
    def _draw_start_state(self) -> None:
        """ Draw elements for START state """
        
        # game title
        pyxel.blt(
            x=140,
            y=45,
            img=0,
            u=0,
            v=128,
            w=160,
            h=64,
            colkey=pyxel.COLOR_PINK,
            scale=2
        )

        # play button
        button_x, button_y = pyxel.width // 2 - 30, pyxel.height // 2 + 50
        button_width, button_height = 60, 15
        button_color_bg_text: tuple[int, int] = (pyxel.COLOR_RED, pyxel.COLOR_WHITE) # format (bg, text)
        
        if button_x <= pyxel.mouse_x <= button_x + button_width and button_y <= pyxel.mouse_y <= button_y + button_height: # if hovered over button
            button_color_bg_text = (pyxel.COLOR_PURPLE, pyxel.COLOR_GRAY)
        # draw button background
        pyxel.rect(x=button_x, y=button_y, w=button_width, h=button_height, col=button_color_bg_text[0])
        
        # button text
        play_text = "PLAY"
        pyxel.text(
            x=button_x + button_width // 2 - len(play_text) * 2,  # Center text in button
            y=button_y + button_height // 2 - 3,  # Center text vertically
            s=play_text,
            col=button_color_bg_text[1],
            font=None
        )

    def _draw_ready_state(self) -> None:
        """ Draws elements for READY state """
        self._draw_ui() # draws the ui


        angle_rad = radians(self.angle) # angle from degrees to radians
        indicator_length = 25  # length of the indicator line
        x_end = self.paddle.x + self.paddle.w / 2 + indicator_length * cos(angle_rad) # the x-coord of the end of the indicator line
        y_end = self.paddle.y - indicator_length * sin(angle_rad) # the y-coord of the end of the indicator line

        # draws the indicator line
        pyxel.line(
            self.paddle.x + self.paddle.w / 2,
            self.paddle.y,
            x_end,
            y_end,
            pyxel.COLOR_WHITE
        )

        self._draw_game_elements()  # draws the paddle, ball, and bricks, and (score objects if any)

        # adds blinking text instruction
        if (pyxel.frame_count // 30) % 2 == 0:  # toggle every 30 frames
            pyxel.text(
                pyxel.width // 2 - 80,  # centered horizontally
                pyxel.height // 2,  # centered vertically
                "Left Mouse Click or Space to Launch!",
                pyxel.COLOR_WHITE,
                None
            )
        
    def _draw_running_state(self) -> None:
        """ Draws the RUNNING state """
        self._draw_game_elements()  # draws the paddle, ball, and bricks
        self._draw_ui() # draws the ui
        
    def _draw_dropped_state(self):
        """Draws the DROPPED state screen."""
        pyxel.cls(pyxel.COLOR_LIGHT_BLUE)  # background

        # ensures the sound plays once when the dropped screen is first drawn
        if self.dropped_timer == 0:  # only plays sound the first frame it starts drawing
            self.sound.play_dropped_sound()  # plays the dropped sound

        # draws calcifer mad/sad
        pyxel.blt(
            x=210,
            y=80,
            img=0,
            w=33,
            h=33,
            u=self.chosen_skin[0],
            v=self.chosen_skin[1],
            colkey=pyxel.COLOR_PINK,
            scale=4
        )
        # draw message
        pyxel.text(
            x=30,
            y=15,
            s=self.chosen_msg,
            col=pyxel.COLOR_BLACK,
            font=None
        )

    def _draw_stage_transition_state(self) -> None:
        """ Draws elements for STAGE_TRANSITION state """
        pyxel.cls(pyxel.COLOR_BLACK)  # background
        message = f"Stage {self.current_stage}"
        pyxel.text(
            pyxel.width // 2 - len(message) * 2.5,  # centers horizontally
            pyxel.height // 2 - 4,  # centers vertically
            message,
            pyxel.COLOR_WHITE,
            None
        )

    def _draw_game_over_state(self) -> None:
        """ Draws the GAME_OVER state """
        
        # "GAME OVER" text
        pyxel.blt(x=139, y=80, img=0, u=48, v=32, w=176, h=16, colkey=pyxel.COLOR_LIGHT_BLUE, scale=2)
        pyxel.text(x=175, y=130, s="Press Enter to Play Again.", col=pyxel.COLOR_BLACK, font=None)
        # display score
        pyxel.text(x=208, y=120,s=f"Score: {self.stats.score}", col=pyxel.COLOR_BLACK, font=None)
    
    def _draw_win_state(self) -> None:
        """ Draws the WIN state """
        # "YOU WIN" text
        pyxel.blt(x=168, y=80, img=0, u=48, v=48, w=136, h=16, colkey=pyxel.COLOR_LIGHT_BLUE, scale=2)
        pyxel.text(x=175, y=130, s="Press Enter to Play Again.", col=pyxel.COLOR_BLACK, font=None)
        # display final score
        pyxel.text(x=208, y=120,s=f"Score: {self.stats.score}", col=pyxel.COLOR_BLACK, font=None) 
        
    def _draw_powerup_timers(self) -> None:
        """ Draws the timers for active power-ups """
        if self.current_game_state in {GameState.READY, GameState.RUNNING}: # only draws timers if running or ready state
            x, y = 10, 60  # starting position for the first timer
            width, height = 60, 6  # dimensions of the timer bar         

            # draws Double Points Timer if active
            if hasattr(self, "double_points_timer"):
                remaining_time = max(0, self.double_points_timer)
                if remaining_time > 0:  # only draws if there's still time left
                    self._draw_timer(x, y, width, height, remaining_time, self.G, "Double Points")
                    y += 15  # space between timers
                else:
                    self._disable_double_points()

            # draws Antigravity Timer if active
            if hasattr(self, "antigravity_timer"):
                remaining_time = max(0, self.antigravity_timer)
                if remaining_time > 0:  # only draws if there's still time left
                    self._draw_timer(x, y, width, height, remaining_time, self.G, "Antigravity")
                else:
                    self._disable_antigravity()

    def _draw_timer(self, x: float, y: float, width: float, height: float, remaining_time: int, max_time: int, label: str) -> None:
        """ Draws a single timer bar with a label """
        # ensures the filled width is clamped between 0 and width
        filled_width = int((remaining_time / max_time) * width) if remaining_time > 0 else 0
        filled_width = min(width, filled_width)  # ensures it never exceeds the bar width
        if remaining_time > 0: # only draws timer if there is still time left  
            # draws label
            pyxel.text(x, y - 7, label, pyxel.COLOR_BLACK, None)

            # draws background bar
            pyxel.rect(x, y, width, height, pyxel.COLOR_BLACK)

            # draws filled portion
            if filled_width > 0:
                pyxel.rect(x, y, filled_width, height, pyxel.COLOR_GREEN)

            # draws border
            pyxel.rectb(x, y, width, height, pyxel.COLOR_WHITE)

            # displays remaining time as text
            time_in_seconds = remaining_time // 60  # Convert frames to seconds
            pyxel.text(x + width + 5, y, f"{time_in_seconds}s", pyxel.COLOR_BLACK, None)
        return

    def _draw_game_elements(self) -> None:
        """ Draws the paddle, ball, and bricks """
        # draws powerup timers (if applicable)
        self._draw_powerup_timers()
        
        # draws paddle
        self.paddle.draw()
        
        # draws all bricks
        for brick in self.bricks:
            brick.draw()
        
        # draws all score objects
        for r in self.score_objects:
            r.draw()
        
        # draws ball/s
        for ball in self.balls:
            ball.draw()

    def _draw_ui(self) -> None:
        """ Draw UI elements like score and lives """
        heart_x: float = 10  # starting x position for hearts
        heart_y: float = 10  # starting y position for hearts (top-left corner)
        heart_spacing: float = 12 # spacing between each heart
        row_limit: int = 10  # max hearts per row

        # Draw hearts for lives
        for i in range(self.stats.lives):
            x = heart_x + (i % row_limit) * heart_spacing  # horizontal position
            y = heart_y + (i // row_limit) * heart_spacing  # vertical position
            pyxel.blt(
                x,  # x position of each heart
                y,  # y position
                0,  # bank
                0,  # u (x coordinate in the asset)
                0,  # v (y coordinate in the asset)
                16,  # width of the heart
                16,  # height of the heart
                pyxel.COLOR_ORANGE  # transparency color
            )
        pyxel.text(pyxel.width - 50, 10, f"Score: {self.stats.score}", pyxel.COLOR_BLACK, None)
    
    def _draw_background(self) -> None:
        """ Draws the background """
        pyxel.blt(
            x=113,
            y=32,
            img=2,
            u=0,
            v=0,
            w=224,
            h=112,
            scale=2.005
        )
        
    def _draw(self) -> None:
        """ General drawing method """
        
        pyxel.cls(pyxel.COLOR_LIGHT_BLUE)
        self._draw_background()
        match self.current_game_state:
            case GameState.START:
                self._draw_start_state()
            case GameState.READY:
                self._draw_ready_state()
            case GameState.RUNNING:
                self._draw_running_state()
            case GameState.DROPPED:
                self._draw_dropped_state()
            case GameState.STAGE_TRANSITION:
                self._draw_stage_transition_state()
            case GameState.GAME_OVER:
                self._draw_game_over_state()
            case GameState.WIN:
                self._draw_win_state()
        
BreakoutGame() # game call
