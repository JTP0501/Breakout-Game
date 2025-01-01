"""
Module Name: main.py

Description:
    Contains the core game logic for "CALCIFER'S COOKOUT", which includes classes for managing 
    the game state, rendering, and interactions.

Author: Josh Patiño
Date: January 01, 2025
"""

import pyxel
import json
from dataclasses import dataclass
from enum import Enum, auto
from math import radians, sin, cos
from random import choice

                                                                # all imported modules
from reward import Reward
from ball import Ball
from paddle import Paddle 
from brick import Brick
from sounds import Sounds

class GameState(Enum):
    """ 
    
    Defines possible game states.

    States:
        START:                  Starts game
        READY:                  Ball/s positioned, waiting for launch
        RUNNING:                Game is running
        DROPPED:                Ball/s out of bounds
        STAGE_TRANSITION:       Handles transitioning of stages
        GAME_OVER:              Player has lost
        WIN:                    Player has won
    """
    START = auto() 
    READY = auto()  
    RUNNING = auto() 
    DROPPED = auto() 
    STAGE_TRANSITION = auto() 
    GAME_OVER = auto() 
    WIN = auto() 

@dataclass
class GameStats:
    """

    Tracks game statisticsc during gameplay.

    Attributes:
        score (int):            Current player score
        lives (int):            Remaining player lives

    """
    score: int = 0                                              # score tracker
    lives: int = 3                                              # lives tracker

class BreakoutGame:
    """
    
    Main game controller class for Breakout implementation.
    
    Attributes:
        gravity (float):                                        gravity felt by game elements
        paddle (Paddle):                                        player-controlled paddle object
        original_paddle_speed (float):                          tracks original paddle speed
        angle (float):                                          tracks angle for the indicator used in READY state
        angle_direction (float):                                tracker for indicator (going left or right)
        angle_cycle_speed (float):                              how fast the degrees are changing per frame
        balls (list[Ball]):                                     contains list of active balls
        P (int):                                                contains the "weight" of each score object's contribution to points from stages.json file
        G (int):                                                contains the duration of the powerups (in seconds)
        X (int):                                                contains the % chance of a score object being a powerup
        Q (int):                                                contains the bonus point increment used in streak logic
        stages (list[dict[str, list[dict[str, int]]]]):         contains all the predefined stages
        g (int):                                                redefined G to match fps
        bricks (list[Brick]):                                   contains all bricks loaded from a stage                                       
        score_objects (list[Reward]):                           contains all score objects that were generated
        current_game_state (GameState):                         tracks the current game state
        sound (Sounds):                                         sound player for sfx and bgm
        dropped_timer (float):                                  timer for DROPPED state
        transition_timer (float):                               timer for STAGE_TRANSITION state
        calcifer_sprites (list[tuple[int, int]]):               contains (u, v) values of sprite (for DROPPED)
        chosen_skin (tuple[int, int]):                          holds the chosen skin from calcifer_sprites
        dropped_msgs (list[str]):                               contains all "messages" calcifer could say
        chosen_msg (str):                                       holds the chosen "message" from dropped_msgs
        streak_count(int):                                      tracks the no. of score objects continuously captured without dropping
        streak_timer(int):                                      tracks remaining duration for streak msg
        
    Methods:
        __init__(self) -> None:
            Initializes a BreakoutGame object when BreakoutGame is called.

        _init_pyxel(cls) -> None:
            * class method
            Initializes pyxel engine.

        _load_stages(cls, file_path: str) -> tuple[int, int, int, int, list[dict[str, list[dict[str, int]]]]]:     
            * class method
            Reads the json file and returns data read.

            Args:
                file_path (str):                                a string containing the path to the json file

        _next_stage(self) -> None:
            Transitions to next stage.

        _start_new_game(self) -> None:
            Starts a new game.

        _reset_ball(self) -> None:
            Prepares ball for launch.
        
        _launch_ball(self) -> None:
            Launches the ball.
        
        _check_collision(self) -> None:
            Handles all collisions.
        
        _check_input(self) -> None:
            Handles user input (depending on the game state).
        
        _spawn_score_objects(self, K: int, brick: Brick) -> None:
            Generates K score objects from the brick.

            Args:
                K (int):                                        the number of score objects to be spawned    
                brick (Brick):                                  the brick that was collided with

        _apply_powerup(self, powerup_type: str) -> None:
            Applies inputted powerup type to the game.

            Args:
                powerup_type (str):                             the powerup type of the score object received

        _update_start_state(self) -> None:
            Listens for play button to be pressed.

        _update_ready_state(self) -> None:
            Handles indicator movement for launch and repositioning of ball to paddle.
        
        _update_running_state(self) -> None:
            Handles ball and streak movement, collisions, and streaks.

        _update_dropped_state(self) -> None:
            Handles "dropped" display and transitioning to next state.

        _update_stage_transition_state(self) -> None:
            Handles "stage transition" display and transitioning to next state.
        
        _update_timers(self) -> None:
            Handles running of power up timers.
        
        _disable_double_points(self) -> None:
            Disables double points power up.
        
        _disable_antigravity(self) -> None:
            Disables antigravity power up.
        
        _update(self) -> None:
            Handles inputs and paddle movement by player, and which updates to run based on current game state.
        
        _draw_start_state(self) -> None:
            Draws a start screen with a play button.
        
        _draw_ready_state(self) -> None:
            Draws the indicator line for launch and instruction,and ui.
        
        _draw_running_state(self) -> None:
            Draws the game elements and ui.

        _draw_dropped_state(self) -> None:
            Draws the dropped screen with the calcifer sprite and message.
        
        _draw_stage_transition_state(self) -> None:
            Draws the stage transitioning screen (Stage: {Stage Count})

        _draw_game_over_state(self) -> None:
            Draws a game over screen and instruction to play again.
        
        _draw_win_state(self) -> None:
            Draws a win screen and instruction to play agiain.
        
        _draw_powerup_timers(self) -> None:
            Draws all the active powerups remaining time.
        
        _draw_timer(self, x: float, y: float, width: float, height: float, remaining_time: int, max_time: int, label: str) -> None:
            Draws a progress bar to represent a timer.

            Args:
                x (float):                                      x-position of timer (top-left corner)
                y (float):                                      y-position of timer (top-left corner)
                width (float):                                  width of timer
                height (float):                                 height of timer
                remaining_time (int):                           how much time is left (in frames)
                max_time (int):                                 the max time that the timer can represent (in frames)
                label (str):                                    the powerup type displayed
        
        _draw_game_elements(self) -> None:
            Draws the paddle, ball/s, and bricks, and the timer and streak if in RUNNING state
        
        _draw_ui(self) -> None:
            Draws the current score and the no. of lives currently.
        
        _draw_background(self) -> None:
            Draws the background image in the resources file.
        
        _draw_streak(self) -> None:
            Displays the current streak no. and the added points.
        
        _draw(self) -> None:
            Draws the background and calls the appropriate drawing method based on the current game state.
        
    
    """
    def __init__(self) -> None:
        """ Constructor """
        self._init_pyxel()                                      # initializes pyxel settings
        self.gravity: float = 0.010
        self.paddle: Paddle = Paddle()                          # initializes a paddle
        self.original_paddle_speed: float = self.paddle.speed
        
        # relates to the indicator when game starts
        self.angle: float                                       # angle tracker for indicator
        self.angle_direction: float                             # 1 is left to right, -1 is right to left
        self.angle_cycle_speed: float                           

        self.balls: list[Ball] = [Ball(self.gravity)]           # initially puts a single ball inside list
        self._reset_ball()                                      # makes sure that ball starts at paddle 

        self.bricks: list[Brick] = []                           # tracks the list of bricks imported from the current stage
        self.score_objects: list[Reward] = []                   # tracks the list of score objects currently at play

        # relates to stage management
        self.P, self.G, self.X, self.Q, self.stages = self._load_stages("../assets/stages.json")
        self.g = self.G * 60                                    # redefines G (60 fps)
        self.current_stage: int                                 # tracks the current stage no. 
        
        self.current_game_state: GameState                      # game state tracker
        self.sound: Sounds = Sounds()                           # sound player
        self.dropped_timer: float = 0                           # timer for DROPPED state
        self.transition_timer: float = 0                        # timer for STAGE_TRANSITION state
        self._start_new_game()                                  # starts a new game
        
        # dropped state prompts
        self.calcifer_sprites: list[tuple[int, int]] = [(48,64), (88, 64)]
        self.chosen_skin: tuple[int, int]                       # tracks calcifer sprite
        self.dropped_msgs: list[str] = [
            "Don't do that again, unless you want to feel my wrath. (T-T)",
            "I am an extremely powerful fire demon, I won't let you humiliate me.",
            "Please, don't drop me again.",
            "What are you doing?!?!?",
            ]
        self.chosen_msg: str

        # relates to streak
        self.streak_count: int = 0
        self.streak_timer: int = 0

        pyxel.run(update=self._update, draw=self._draw)                     # runs game loop
  
    @classmethod
    def _init_pyxel(cls) -> None:
        """ Initializes Pyxel engine settings """

        pyxel.init(width=450, height=200, display_scale=3, title="Breakout Game", fps=60)
        pyxel.load(filename="../assets/resources.pyxres")                # our resource file

    # +++++++++++++++++++++++++++++++++ STAGE MANAGEMENT +++++++++++++++++++++++++++++++++

    @classmethod
    def _load_stages(cls, file_path: str) -> tuple[int, int, int, int, list[dict[str, list[dict[str, int]]]]]:
        """ Load stages from JSON file """
        with open(file_path, "r") as f:
            data = json.load(f)
        return data["P"], data["G"], data["X"], data["Q"], data["stages"]

    def _load_stage(self, stage_index: int) -> None:
        """ Load a specific stage """
        stage = self.stages[stage_index]                        # stages is 0-indexed
        self.bricks = [
            Brick(brick["x"], brick["y"], brick["brick_type"], K=pyxel.rndi(a=2,b=4))
            for brick in stage["bricks"]
        ]

    def _next_stage(self) -> None:
        """ Move to the next stage """
        if self.current_stage < len(self.stages):
            self.current_stage += 1
            self.transition_timer = pyxel.frame_count           # snapshot of frame count
            self.streak_count = 0                               # resets streak after each stage cleared
            self.streak_timer = 0 
            self.current_game_state = GameState.STAGE_TRANSITION
        else:
            self.current_game_state = GameState.WIN

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++

    def _start_new_game(self) -> None:
        """ Starts a new game """
        pyxel.stop(ch=1)                                        # mutes channel 1 sounds that were still playing (sound fx)
        self.stats = GameStats()
        self.paddle.speed = self.original_paddle_speed          # resets paddle speed
        self.score_objects.clear()                              # resets score objects tracker
        self.bricks.clear()                                     # resets old bricks (if there are any)
        self.current_stage = 1                                  # sets the current stage to the first one (1-indexed)
        self.transition_timer = 0                               
        self._load_stage(self.current_stage - 1)                # loads the current stage
        self._reset_ball()                                      # resets ball position to paddle
        self.current_game_state = GameState.START 
        self.sound.game_over_played = False 
        self.sound.win_played = False 
        pyxel.mouse(visible=True)                                       # enables mouse cursor view
        pyxel.playm(msc=0, loop=True)                               # plays bgm
        
    def _reset_ball(self):
        """ Resets the ball to paddle """
        while len(self.balls) > 1:
            self.balls.pop()                                    # leaves a single ball
        
        self.balls[0].clear_trails()                            # removes trails that could still be up
        self.balls[0].x = self.paddle.x + self.paddle.w / 2 - self.balls[0].r 
        self.balls[0].y = self.paddle.y - self.balls[0].r * 2    
        
        self.angle = 0                                          # starts looking right
        self.angle_direction = 1 
        self.angle_cycle_speed = 2

        # ball is not launched yet
        self.balls[0].speed_x = 0 
        self.balls[0].speed_y = 0

        # resets ball's out of bounds state
        self.balls[0].out_of_bounds = False

    def _launch_ball(self):
        """ Launches the ball based on the current angle """
        angle_rad: float = radians(self.angle)
        self.balls[0].speed_x = cos(angle_rad) * 2.5
        self.balls[0].speed_y = -sin(angle_rad) * 2.5

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
            for i in reversed(range(len(self.bricks))):         # checks all bricks for collisions
                b: Brick = self.bricks[i]

                brick_collision = ball.detect_collision(b)
                if brick_collision:
                    self.sound.play_ball_hit_sound()
                    
                    if ball.destroy_brick:
                        if b.brick_type == 5:                   # if it is a ball maker   
                            new_ball = Ball(self.gravity)       # new ball is made
                            # angle in radians
                            angle = radians(pyxel.rndi(a=0, b=360))
                            speed = pyxel.rndf(a=1,b=new_ball.MAX_SPEED)

                            # sets speed in the x and y direction
                            new_ball.speed_x = speed * cos(angle)
                            new_ball.speed_y = -speed * sin(angle)

                            # positions ball at the center of brick
                            new_ball.x = b.x + (b.w / 2)  
                            new_ball.y = b.y + (b.h / 2)

                            self.balls.append(new_ball)  # adds new ball to the game
                            # Note: added ball doesn't carry over to the next stages or if goes into dropped state
                        else:
                            # if not a ball maker, spawns K score objects
                            self._spawn_score_objects(b.K, b)
                        del self.bricks[i]                      # removes collided with destructible bricks
                        ball.destroy_brick = False              # reset
                    break
    
        # Reward vs World (Paddle and Bottom)
        for i in reversed(range(len(self.score_objects))):
            r = self.score_objects[i]
            collision_type, points = r.collides(self.paddle)
            if collision_type is not None: # if it collides
                if collision_type == "paddle":
                    self.sound.play_reward_sound()
                    self.streak_count += 1
                    self.streak_timer = 60                      # displays streak message for 1 second (60 frames)

                    # calculates added points with streak multiplier
                    streak_bonus = (self.streak_count - 1) * self.Q  
                    added_points = points + streak_bonus
                    
                    if r.powerup_type: # if it is a powerup
                        self._apply_powerup(r.powerup_type)
                    # checks if the timer is there and double points is set to True
                    if hasattr(self, "double_points_timer") and self.double_points:
                        added_points *= 2                       # doubles the points of objects collided with (including the added bonus)
                    self.stats.score += added_points
                else:
                    self.streak_count = 0                       # resets streak
                    self.streak_timer = 0                       # clears streak display
                del self.score_objects[i]
                
    def _check_input(self) -> None:
        """ Checks for inputs by user (depending on the game state)"""
        if self.current_game_state == GameState.READY:
             # press left mouse click or space bar to launch ball
            if pyxel.btnp(key=pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(key=pyxel.KEY_SPACE):
                self.sound.play_launch_sound()
                self._launch_ball()                             # launches the ball
    
        if self.current_game_state in {GameState.GAME_OVER, GameState.WIN}:
            # press enter to start a new game
            if pyxel.btnp(key=pyxel.KEY_RETURN): 
                self._start_new_game()
                pyxel.playm(msc=0, loop=True)                       # restarts background music

    def _spawn_score_objects(self, K: int, brick: Brick) -> None:
        """ Spawns K rectangular score objects within the bounds of a hit brick """
        
        # brick properties
        brick_x, brick_y = brick.x, brick.y                     # top-left corner of the brick

        # score object properties
        obj_width = 8                                          
        obj_height = 10                                         
        padding = 2                                             # space between objects

        # defines positions for up to 4 objects (manual layout)
        positions = [
        (brick_x + padding, brick_y + padding),                              # 1st
        (brick_x + obj_width + padding, brick_y + padding),                  # 2nd
        (brick_x + padding, brick_y + 2 * obj_height + padding),             # 3rd
        (brick_x + obj_width + padding, brick_y + 2 * obj_height + padding)  # 4th
        ]

        # spawns K objects
        for i in range(K):
            spawn_x, spawn_y = positions[i]                     # uses predefined positions directly

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
        if powerup_type == "life_up":                           # (*carries over)
            self.stats.lives += 1                               
        elif powerup_type == "antigravity":                     # has duration G (*doesn't carry over)
            for ball in self.balls:
                ball.gravity = 0                                
            if hasattr(self, "antigravity_timer"):              
                self.antigravity_timer += self.g
            else:                
                self.antigravity_timer = self.g                 
        elif powerup_type == "paddle_speed":                    # (*carries over)
            self.paddle.speed += 0.20              
        elif powerup_type == "double_points":                   # has duration G (*doesn't carry over)
            self.double_points = True                           
            if hasattr(self, "double_points_timer"):
                self.double_points_timer += self.g              
            else:
                self.double_points_timer = self.g  

# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def _update_start_state(self) -> None:
        """ Update logic for START state """
        # transitions to READY state when the player presses the Play button
        if pyxel.btnp(key=pyxel.MOUSE_BUTTON_LEFT):                 # left mouse click on button to start
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y

                                                                # checks if the mouse is within the Play button areas
            button_x, button_y = pyxel.width // 2 - 30, pyxel.height // 2 + 50
            button_width, button_height = 60, 15

            if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                pyxel.mouse(visible=False) 
                self.transition_timer = pyxel.frame_count
                self.current_game_state = GameState.STAGE_TRANSITION
                self.sound.play_clicked_button_sound()
                
    def _update_ready_state(self) -> None:
        """ Update logic for READY state """
        # repositions ball
        self.balls[0].x = self.paddle.x + self.paddle.w / 2 - self.balls[0].r

        # oscillates the angle left to right, then right to left
        self.angle += self.angle_direction * self.angle_cycle_speed

        # reverses direction at bounds
        if self.angle == 180 or self.angle == 0:
            self.angle_direction = -self.angle_direction        # reversed direction
    
    def _update_running_state(self) -> None:
        """ Update logic for RUNNING state """
        if self.streak_timer > 0:
            self.streak_timer -= 1

        self._update_timers()

        for ball in self.balls:
            ball.update()                                       # moves the ball
        
        for r in self.score_objects:                            # moves the score objects
            r.update()

        self._check_collision()                                 # checks for collisions
        
        # if all bricks cleared not including indestructible brick (stage cleared)
        if not self.bricks or all(brick.brick_type == 4 for brick in self.bricks): 
            if not self.score_objects:                          # if there are no score objects in the screen
                if hasattr(self, "antigravity_timer"):
                    self._disable_antigravity()
                if hasattr(self, "double_points"):
                    self._disable_double_points()
                if self.current_stage == len(self.stages):      # last stage cleared
                    self.current_game_state = GameState.WIN
                    pyxel.stop()
                else:
                    self._next_stage()

                                                                # removes all balls that are out of bounds
        if len(self.balls) > 1:
            self.balls = [ball for ball in self.balls if not ball.out_of_bounds]

                                                                # checks if all balls are out of bounds
        if len(self.balls) == 1:                                # checks if there is only one ball left
            if self.balls[0].out_of_bounds:                     # checks if that singular ball is out of bounds
                self.chosen_skin = choice(self.calcifer_sprites)  
                self.chosen_msg = choice(self.dropped_msgs)  
                self.stats.lives -= 1
                if self.stats.lives > 0:
                    self.current_game_state = GameState.DROPPED
                else:
                    self.current_game_state = GameState.GAME_OVER
                    pyxel.stop()  
                 
    def _update_dropped_state(self) -> None:
        """ Updates logic for DROPPED state """
                                                                # shows DROPPED screen and resets the ball after a delay
        if self.dropped_timer == 0:
            self.dropped_timer = pyxel.frame_count  

                                                                # waits for 120 frames (2 seconds at 60 FPS)
        if pyxel.frame_count - self.dropped_timer > 120:
            # resets
            self.dropped_timer = 0 
            self._reset_ball()  
            self.current_game_state = GameState.READY

    def _update_stage_transition_state(self) -> None:
        """ Update logic for STAGE_TRANSITION state """
                                                                # waits for 120 frames (2 seconds at 60 FPS)
        if pyxel.frame_count - self.transition_timer > 120:
            self._load_stage(self.current_stage - 1)            # loads the next stage
            self._reset_ball()
            self.current_game_state = GameState.READY
    
    def _update_timers(self) -> None:
        """ Update timers based on game state """
        if self.current_game_state == GameState.RUNNING:
            if hasattr(self, "double_points_timer"):
                self.double_points_timer -= 1                   # decrements timer in RUNNING state
            if hasattr(self, "antigravity_timer"):
                self.antigravity_timer -= 1                     # decrements timer in RUNNING state
    
    def _disable_double_points(self) -> None:
        """ Disables double points power up"""
        self.double_points = False                              # deactivates double points
        if hasattr(self, "double_points_timer"):
            del self.double_points_timer                        # removes the timer
    
    def _disable_antigravity(self) -> None:
        """ Disables antigravity power up """
        for ball in self.balls:
            ball.gravity = self.gravity                         # restores gravity for all balls
        if hasattr(self, "antigravity_timer"):
            del self.antigravity_timer                          # removes the timer

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
        # format: (bg, text)
        button_color_bg_text: tuple[int, int] = (pyxel.COLOR_RED, pyxel.COLOR_WHITE) 
        
        if button_x <= pyxel.mouse_x <= button_x + button_width and button_y <= pyxel.mouse_y <= button_y + button_height: # if hovered over button
            button_color_bg_text = (pyxel.COLOR_PURPLE, pyxel.COLOR_GRAY)
                                                                # draw button background
        pyxel.rect(x=button_x, y=button_y, w=button_width, h=button_height, col=button_color_bg_text[0])
        
                                                                # button text
        play_text = "PLAY"
        pyxel.text(
            x=button_x + button_width // 2 - len(play_text) * 2,
            y=button_y + button_height // 2 - 3,                
            s=play_text,
            col=button_color_bg_text[1],
            font=None
        )

    def _draw_ready_state(self) -> None:
        """ Draws elements for READY state """
        self._draw_ui()                                         # draws the ui


        angle_rad = radians(self.angle)
        indicator_length = 25  
        x_end = self.paddle.x + self.paddle.w / 2 + indicator_length * cos(angle_rad) 
        y_end = self.paddle.y - indicator_length * sin(angle_rad) 

                                                                # draws the indicator line
        pyxel.line(
            x1=self.paddle.x + self.paddle.w / 2,
            y1=self.paddle.y,
            x2=x_end,
            y2=y_end,
            col=pyxel.COLOR_WHITE
        )

        self._draw_game_elements()                              # draws the paddle, ball, and bricks, and (score objects if any)

                                                                # adds blinking text instruction
        if (pyxel.frame_count // 30) % 2 == 0:                  # toggles every 30 frames  
            pyxel.text(
                x=pyxel.width // 2 - 80,  
                y=pyxel.height // 2,  
                s="Left Mouse Click or Space to Launch!",
                col=pyxel.COLOR_WHITE,
                font=None
            )
        
    def _draw_running_state(self) -> None:
        """ Draws the RUNNING state """
        self._draw_game_elements()                              # draws the paddle, ball, and bricks
        self._draw_ui()                                         # draws the ui
        
    def _draw_dropped_state(self) -> None:
        """Draws the DROPPED state screen."""
        pyxel.cls(col=pyxel.COLOR_LIGHT_BLUE)                   # background

        if self.dropped_timer == 0:                             # only plays sound the first frame it starts drawing
            self.sound.play_dropped_sound()        

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
                                                                # draws message
        pyxel.text(
            x=30,
            y=15,
            s=self.chosen_msg,
            col=pyxel.COLOR_BLACK,
            font=None
        )

    def _draw_stage_transition_state(self) -> None:
        """ Draws elements for STAGE_TRANSITION state """
        pyxel.cls(col=pyxel.COLOR_BLACK)                        # background
        message = f"Stage {self.current_stage}"
        pyxel.text(
            x=pyxel.width // 2 - len(message) * 2.5,  
            y=pyxel.height // 2 - 4,  
            s=message,
            col=pyxel.COLOR_WHITE,
            font=None
        )

    def _draw_game_over_state(self) -> None:
        """ Draws the GAME_OVER state """
        
                                                                # "GAME OVER" text
        pyxel.blt(x=139, y=80, img=0, u=48, v=32, w=176, h=16, colkey=pyxel.COLOR_LIGHT_BLUE, scale=2)
        pyxel.text(x=175, y=130, s="Press Enter to Play Again.", col=pyxel.COLOR_BLACK, font=None)
                                                                # displays score
        pyxel.text(x=208, y=120,s=f"Score: {self.stats.score}", col=pyxel.COLOR_BLACK, font=None)
    
    def _draw_win_state(self) -> None:
        """ Draws the WIN state """
                                                                # "YOU WIN" text
        pyxel.blt(x=168, y=80, img=0, u=48, v=48, w=136, h=16, colkey=pyxel.COLOR_LIGHT_BLUE, scale=2)
        pyxel.text(x=175, y=130, s="Press Enter to Play Again.", col=pyxel.COLOR_BLACK, font=None)
                                                                # displays final score
        pyxel.text(x=208, y=120,s=f"Score: {self.stats.score}", col=pyxel.COLOR_BLACK, font=None) 
        
    def _draw_powerup_timers(self) -> None:
        """ Draws the timers for active power-ups """
        if self.current_game_state in {GameState.READY, GameState.RUNNING}:
            x, y = 10, 60                                       # starting position for the first timer
            width, height = 60, 6                               # dimensions of the timer bar         

                                                                # draws Double Points Timer if active
            if hasattr(self, "double_points_timer"):
                remaining_time = max(0, self.double_points_timer)
                if remaining_time > 0:                          
                    self._draw_timer(x, y, width, height, remaining_time, self.g, "Double Points")
                    y += 15                                     # space between timers
                else:
                    self._disable_double_points()

                                                                # draws Antigravity Timer if active
            if hasattr(self, "antigravity_timer"):
                remaining_time = max(0, self.antigravity_timer)
                if remaining_time > 0:                  
                    self._draw_timer(x, y, width, height, remaining_time, self.g, "Antigravity")
                else:
                    self._disable_antigravity()

    def _draw_timer(self, x: float, y: float, width: float, height: float, remaining_time: int, max_time: int, label: str) -> None:
        """ Draws a single timer bar with a label """
                                                                # ensures the filled width is clamped between 0 and width
        filled_width = int((remaining_time / max_time) * width) if remaining_time > 0 else 0
        filled_width = min(width, filled_width)                 # ensures it never exceeds the bar width
        if remaining_time > 0:                                  # only draws timer if there is still time left  
                                                                # draws label
            pyxel.text(x=x, y=y - 7, s=label, col=pyxel.COLOR_BLACK, font=None)

                                                                # draws background bar
            pyxel.rect(x=x, y=y, w=width, h=height, col=pyxel.COLOR_BLACK)

                                                                # draws filled portion
            if filled_width > 0:
                pyxel.rect(x=x, y=y, w=filled_width, h=height, col=pyxel.COLOR_GREEN)

                                                                # draws border
            pyxel.rectb(x=x, y=y, w=width, h=height, col=pyxel.COLOR_WHITE)

                                                                # displays remaining time as text
            time_in_seconds = remaining_time // 60              # frames to seconds
            pyxel.text(x=x + width + 5, y=y, s=f"{time_in_seconds}s", col=pyxel.COLOR_BLACK, font=None)
        return

    def _draw_game_elements(self) -> None:
        """ Draws the paddle, ball/s, and bricks """
        # checks if game state is RUNNING state
        if self.current_game_state == GameState.RUNNING:
                                                                # draws paddle speed when game is in RUNNING
            pyxel.text(x=10,y=pyxel.height - 10, s=f"Paddle Speed: {"%.2f" % self.paddle.speed}", col=pyxel.COLOR_BLACK, font=None) 
                                                                # draws streak
            self._draw_streak()

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
        heart_x: float = 10                                     # starting pos for hearts
        heart_y: float = 10  
        heart_spacing: float = 12                               # spacing between each heart
        row_limit: int = 8                                      # max hearts per row

                                                                # draws hearts for lives
        for i in range(self.stats.lives):
            x = heart_x + (i % row_limit) * heart_spacing       
            y = heart_y + (i // row_limit) * heart_spacing      
            pyxel.blt(
                x=x,  
                y=y,  
                img=0,  
                u=0,  
                v=0,  
                w=16,  
                h=16,  
                colkey=pyxel.COLOR_ORANGE  
            )
                                                                # draws score
        pyxel.text(x=pyxel.width - 50, y=10, s=f"Score: {self.stats.score}", col=pyxel.COLOR_BLACK, font=None)
    
    def _draw_background(self) -> None:
        """ Draws the background """
        
                                                                # draws background image
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
    
    def _draw_streak(self) -> None:
        """ Draws impact of each score object received """

        points: int = self.P + ((self.streak_count - 1) * self.Q)
        if hasattr(self, "double_points_timer"):                # checks if double points is active
            points *= 2
        
        if self.streak_count > 1 and self.streak_timer > 0:
                                                                # draws streak
            pyxel.text(
                x=10, 
                y=40,
                s=f"Streak: {self.streak_count} (+{points})",
                col=pyxel.COLOR_ORANGE,
                font=None
            )

    def _draw(self) -> None:
        """ General drawing method """
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
