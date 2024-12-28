import pyxel
import json

from enum import Enum, auto
from math import radians, sin, cos
from dataclasses import dataclass

from ball import Ball
from paddle import Paddle 
from brick import Brick


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
        self.gravity: float = 0.007
        self.stats: GameStats # holds game stats
         
        self.paddle: Paddle = Paddle() # initializes a paddle
        # relates to the indicator when game starts
        self.angle: float # angle tracker for indicator
        self.angle_direction: float # 1 is left to right, -1 is right to left
        self.angle_cycle_speed: float # degrees per frame     

        self.ball: Ball = Ball(self.gravity) # initializes a ball 
        self._reset_ball() # makes sure that ball starts at paddle 

        self.stages: list[dict[str, list[dict[str, int]]]] = self._load_stages("../assets/stages.json") # contains all the predefined stages
        self.current_stage: int # tracks the current stage no. 
        self.bricks: list[Brick] = [] # tracks the list of bricks imported from the current stage

        self.current_game_state: GameState # game state tracker
        self._start_new_game() # starts a new game
        self.dropped_timer: float = 0  # timer for DROPPED state
        self.transition_timer: float = 0 # time for STAGE_TRANSITION state

        pyxel.run(self._update, self._draw) # runs game loop

    @classmethod
    def _init_pyxel(cls) -> None:
        """ Initializes Pyxel engine settings """
        pyxel.init(width=450, height=200, display_scale=3, title="Breakout Game", fps=60)
        pyxel.load("../assets/resources.pyxres") # our resource file

    # +++++++++++++++++++++++++++++++++ STAGE MANAGEMENT +++++++++++++++++++++++++++++++++

    @classmethod
    def _load_stages(cls, file_path: str) -> list[dict[str, list[dict[str, int]]]]:
        """ Load stages from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return data["stages"]

    def _load_stage(self, stage_index: int) -> None:
        """ Load a specific stage."""
        stage = self.stages[stage_index] # stages is 0-indexed
        self.bricks = [
            Brick(brick["x"], brick["y"], brick["brick_type"])
            for brick in stage["bricks"]
        ]

    def _next_stage(self) -> None:
        """ Move to the next stage."""
        if self.current_stage < len(self.stages):
            self.current_stage += 1
            self.current_game_state = GameState.STAGE_TRANSITION
            self.transition_timer = pyxel.frame_count  # initializes the transition timer
        else:
            self.current_game_state = GameState.WIN

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++

    def _start_new_game(self) -> None:
        """ Starts a new game """
        self.stats = GameStats() # initializes a GameStats object for new game
        self.current_stage = 1 # sets the current stage to the first one (1-indexed)
        self._load_stage(self.current_stage - 1) # loads the current stage
        self._reset_ball() # resets ball position to paddle
        self.current_game_state = GameState.START # sets the gamestate to the START state
        pyxel.mouse(True) # enable mouse cursor view
        
    def _reset_ball(self):
        """ Resets the ball to paddle """
        self.ball.clear_trails() # removes trails that could still be up
        self.ball.x = self.paddle.x + self.paddle.w / 2 - self.ball.r  # center on paddle
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
        collision: bool = self.ball.detect_collision(self.paddle, is_paddle=True)
        
        # Ball vs Bricks
        for i in reversed(range(len(self.bricks))): # checks all bricks for collisions
            b: Brick = self.bricks[i]
            collision = self.ball.detect_collision(b)
            if collision:
                if b.hit():
                    del self.bricks[i] # removes brick that collides with ball and has no health
                break

    def _check_input(self) -> None:
        """ Checks for inputs by user (depending on the game state)"""
        if self.current_game_state == GameState.READY:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self._launch_ball() # launches the ball
    
        if self.current_game_state in {GameState.GAME_OVER, GameState.WIN}:
            if pyxel.btnp(pyxel.KEY_RETURN): # press enter to start a new game
                self._start_new_game()

# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def _update_start_state(self) -> None:
        """ Update logic for START state """
        # transitions to READY state when the player presses the Play button
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):  # Mouse click to start
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y

            # checks if the mouse is within the Play button area
            button_x, button_y = pyxel.width // 2 - 30, pyxel.height // 2 + 50
            button_width, button_height = 60, 15

            if button_x <= mouse_x <= button_x + button_width and button_y <= mouse_y <= button_y + button_height:
                pyxel.mouse(False) # disable mouse cursor view
                self.current_game_state = GameState.STAGE_TRANSITION

    def _update_ready_state(self) -> None:
        """ Update logic for READY state """
        self.ball.x = self.paddle.x + self.paddle.w / 2 - self.ball.r # centers the ball at the paddle's horizontal center

        # Oscillate the angle left to right, then right to left
        self.angle += self.angle_direction * self.angle_cycle_speed

        # Reverse direction at bounds
        if self.angle == 180 or self.angle == 0:
            self.angle_direction = -self.angle_direction # reversed direction
    
    def _update_running_state(self) -> None:
        """ Update logic for RUNNING state """
        self.ball.update() # moves the ball
        self._check_collision() # checks for collisions
        # 4 is indestructible
        if not self.bricks or all(brick.brick_type == 4 for brick in self.bricks): # all bricks cleared (stage cleared)
            if self.current_stage == len(self.stages): # last stage cleared
                self.current_game_state = GameState.WIN
            else:
                self._next_stage()

        if self.ball.out_of_bounds: # if ball dropped
            self.current_game_state = GameState.DROPPED
    
    def _update_dropped_state(self) -> None:
        """ Updates logic for DROPPED state """
        # checks if there are lives remaining
        if self.stats.lives > 1:
            # shows DROPPED screen and resets the ball after a delay
            if self.dropped_timer == 0:
                self.dropped_timer = pyxel.frame_count  # initializes the timer

            # waits for 120 frames (2 seconds at 60 FPS)
            if pyxel.frame_count - self.dropped_timer > 120:
                self.dropped_timer = 0  # resets the timer
                self.stats.lives -= 1
                self._reset_ball()  # resets the ball position
                self.current_game_state = GameState.READY
        else:
            # transitions directly to GAME_OVER if no lives remain
            self.stats.lives = 0  # Ensures lives don't go negative
            self.current_game_state = GameState.GAME_OVER

    def _update_stage_transition_state(self) -> None:
        """ Update logic for STAGE_TRANSITION state """
        # waits for 120 frames (2 seconds at 60 FPS)
        if pyxel.frame_count - self.transition_timer > 120:
            self._load_stage(self.current_stage - 1)  # loads the next stage
            self._reset_ball()  # resets the ball to the paddle
            self.current_game_state = GameState.READY

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
                pass # to be added
            case GameState.WIN:
                pass # to be added 

# +++++++++++++++++++++++++++++++++ DRAW METHODS +++++++++++++++++++++++++++++++++
    def _draw_start_state(self) -> None:
        """ Draw elements for START state """
        #background color
        pyxel.cls(pyxel.COLOR_LIGHT_BLUE)
        
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

        # draw button background
        pyxel.rect(button_x, button_y, button_width, button_height, pyxel.COLOR_RED)

        # button text
        play_text = "PLAY"
        pyxel.text(
            button_x + button_width // 2 - len(play_text) * 2,  # Center text in button
            button_y + button_height // 2 - 3,  # Center text vertically
            play_text,
            pyxel.COLOR_WHITE,
            None
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
            pyxel.COLOR_RED
        )

        # adds blinking text instruction
        if (pyxel.frame_count // 30) % 2 == 0:  # toggle every 30 frames
            pyxel.text(
                pyxel.width // 2 - 50,  # centered horizontally
                pyxel.height // 2,  # centered vertically
                "Left Mouse Click to Launch!",
                pyxel.COLOR_BLACK,
                None
            )
        self._draw_game_elements()  # draws the paddle, ball, and bricks
        
    def _draw_running_state(self) -> None:
        """ Draws the RUNNING state """
        self._draw_game_elements()  # draws the paddle, ball, and bricks
        self._draw_ui() # draws the ui
    
    def _draw_dropped_state(self):
        """Draws the DROPPED state screen."""
        pyxel.cls(pyxel.COLOR_LIGHT_BLUE)  # background
        pyxel.text(
            pyxel.width // 2 - 50,
            pyxel.height // 2,
            "BALL DROPPED!",
            pyxel.COLOR_BLACK,
            None
        )
    def _draw_stage_transition_state(self) -> None:
        """ Draws elements for STAGE_TRANSITION state """
        pyxel.cls(pyxel.COLOR_LIGHT_BLUE)  # background
        message = f"Stage {self.current_stage}"
        pyxel.text(
            pyxel.width // 2 - len(message) * 2.5,  # center horizontally
            pyxel.height // 2 - 4,  # center vertically
            message,
            pyxel.COLOR_BLACK,
            None
        )

    def _draw_game_over_state(self) -> None:
        """ Draws the GAME_OVER state """
        
        # "GAME OVER" text
        pyxel.blt(x=139, y=80, img=0, u=48, v=32, w=176, h=16, colkey=pyxel.COLOR_LIGHT_BLUE, scale=2)
        pyxel.text(x=175, y=130, s="Press Enter to Play Again.", col=pyxel.COLOR_BLACK, font=None)
    
    def _draw_win_state(self) -> None:
        """ Draws the WIN state """
        # "YOU WIN" text
        pyxel.blt(x=168, y=80, img=0, u=48, v=48, w=136, h=16, colkey=pyxel.COLOR_LIGHT_BLUE, scale=2)
        pyxel.text(x=175, y=130, s="Press Enter to Play Again.", col=pyxel.COLOR_BLACK, font=None)
        # display final score
        
    def _draw_game_elements(self) -> None:
        """ Draws the paddle, ball, and bricks """
        self.paddle.draw()
        for brick in self.bricks:
            brick.draw()
        self.ball.draw()
    
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
        pyxel.text(10, pyxel.height - 20, f"Score: {self.stats.score}", pyxel.COLOR_BLACK, None)
        
    def _draw(self) -> None:
        """ General drawing method """

        pyxel.cls(pyxel.COLOR_LIGHT_BLUE)

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
