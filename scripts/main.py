import pyxel
from enum import Enum, auto
import json
from math import radians, sin, cos
from dataclasses import dataclass

from ball import Ball
from paddle import Paddle 
from brick import Brick


class GameState(Enum):
    """ Game states enumeration """
    READY = auto() # Ready to start 
    RUNNING = auto() # In progress
    DROPPED = auto() # Ball out of bounds 
    GAME_OVER = auto() # Player lost the game
    WIN = auto() # Player won the game

@dataclass
class GameStats:
    score: int = 0
    lives: int = 3

class BreakoutGame:
    def __init__(self) -> None:
        """ Constructor """

        self._init_pyxel()
        self.stats: GameStats
        
        self.paddle = Paddle()
        self.angle: float = 0
        self.angle_direction: float = 1  # 1 for increasing, -1 for decreasing
        self.angle_cycle_speed: float = 2  # Degrees per frame     

        self.ball = Ball()
        self._reset_ball()

        self.stages: list[dict[str, list[dict[str, int]]]] = self._load_stages("../assets/stages.json")
        self.current_stage: int
        self.bricks: list[Brick] = []

        self.current_game_state = GameState.READY # game state tracker
        self._start_new_game() # starts a new game

        pyxel.run(self._update, self._draw)

    @classmethod
    def _init_pyxel(cls) -> None:
        """ Initializes Pyxel engine settings """
        pyxel.init(width=600, height=300, display_scale=2, title="Breakout Game", fps=60)
        pyxel.load("../assets/resources.pyxres")

    @classmethod
    def _load_stages(cls, file_path: str) -> list[dict[str, list[dict[str, int]]]]:
        """ Load stages from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return data["stages"]

    def _load_stage(self, stage_index: int) -> None:
        """ Load a specific stage."""
        stage = self.stages[stage_index]
        self.bricks = [
            Brick(brick["x"], brick["y"], brick["brick_type"])
            for brick in stage["bricks"]
        ]

    def _next_stage(self) -> None:
        """ Move to the next stage."""
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            self._load_stage(self.current_stage)
            self._reset_ball()
            self.current_game_state = GameState.READY
        else:
            self.current_game_state = GameState.WIN

    def _start_new_game(self) -> None:
        """ Starts a new game """
        self.stats = GameStats()
        self.current_stage = 0
        self._load_stage(self.current_stage)
        self._reset_ball()
        self.current_game_state = GameState.READY

    def _reset_ball(self):
        """ Resets the ball to paddle """
        self.ball.x = self.paddle.x + self.paddle.w / 2
        self.ball.y = self.paddle.y - self.ball.r
        self.angle = 0
        self.angle_direction = 1
        self.ball.speed_x = 0
        self.ball.speed_y = 0
        self.ball.out_of_bounds = False

    def _launch_ball(self):
        """ Launches the ball based on the current angle """
        angle_rad = radians(self.angle)
        self.ball.speed_x = cos(angle_rad) * 2.5
        self.ball.speed_y = -sin(angle_rad) * 2.5

        if self.current_game_state == GameState.RUNNING:
            self.ball.update()
            self._check_collision()

            if not self.bricks: # Level Cleared
                if self.current_stage == len(self.stages) - 1:  # Last stage cleared
                    self.current_game_state = GameState.WIN
                else:
                    self._next_stage()

            if self.ball.out_of_bounds:
                self.stats.lives -= 1
                if self.stats.lives > 0:
                    self.current_game_state = GameState.DROPPED
                else:
                    self.current_game_state = GameState.GAME_OVER

    def _update_ready_state(self) -> None:
        """ Update logic for READY state """
        self.angle += self.angle_direction * self.angle_cycle_speed
        self.ball.x = self.paddle.x + self.paddle.w / 2

        if self.angle > 180:
            self.angle = 180
            self.angle_direction = -1 # Decreasing (right)
        elif self.angle < 0:
            self.angle = 0
            self.angle_direction = 1 # Increasing (left)
    
    def _update_running_state(self) -> None:
        """ Update logic for RUNNING state """
        self.ball.update()
        self._check_collision()

        if not self.bricks: # All bricks cleared (stage cleared)
            if self.current_stage == len(self.stages) - 1: # Last stage cleared
                self.current_game_state = GameState.WIN
            else:
                self._next_stage()

        if self.ball.out_of_bounds:
            self.stats.lives -= 1
            self.current_game_state = GameState.DROPPED if self.stats.lives > 0 else GameState.GAME_OVER
    
    def _update_dropped_state(self) -> None:
        """ Update logic for DROPPED state """
        if self.stats.lives > 0:
            self.current_game_state = GameState.READY
            self._reset_ball()
        else:
            self.current_game_state = GameState.GAME_OVER

    def _check_collision(self) -> None:
        """ Checks for all kinds of collisions """
        # Ball vs Paddle
        collision: bool = self.ball.detect_collision(self.paddle, paddle=True)[0]
        if collision:
            pass
        # Ball vs Bricks
        for i in reversed(range(len(self.bricks))):
            b: Brick = self.bricks[i]
            collision, score = self.ball.detect_collision(b)
            if collision:
                self.stats.score += score
                del self.bricks[i]
                break

    def _check_input(self) -> None:
        """ Checks for inputs by user (depending on the game state)"""
        if self.current_game_state in {GameState.READY, GameState.DROPPED}:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                self._launch_ball()
                self.current_game_state = GameState.RUNNING
    
        if self.current_game_state == GameState.GAME_OVER or self.current_game_state == GameState.WIN:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self._start_new_game()
    
    def _draw_ready_state(self) -> None:
        """ Draw logic for READY state """
        angle_rad = radians(self.angle)
        indicator_length = 20  # Length of the indicator line
        x_end = self.paddle.x + self.paddle.w / 2 + indicator_length * cos(angle_rad)
        y_end = self.paddle.y - indicator_length * sin(angle_rad)

        # Draw the indicator
        pyxel.line(
            self.paddle.x + self.paddle.w / 2,
            self.paddle.y,
            x_end,
            y_end,
            pyxel.COLOR_GRAY
        )
    
    def _draw_game_elements(self) -> None:
        """ Draw paddle, ball, and bricks """
        self.paddle.draw()
        for brick in self.bricks:
            brick.draw()
        self.ball.draw()
    
    def _draw_ui(self) -> None:
        """ Draw UI elements like score and lives """
        pyxel.text(10, pyxel.height - 30, f"Lives: {self.stats.lives}", pyxel.COLOR_WHITE, None)
        pyxel.text(10, pyxel.height - 20, f"Score: {self.stats.score}", pyxel.COLOR_WHITE, None)

    def _update(self) -> None:
        """ General update method """
        self._check_input()
        self.paddle.update()

        match self.current_game_state:
            case GameState.READY:
                self._update_ready_state()
            case GameState.RUNNING:
                self._update_running_state()
            case GameState.DROPPED:
                self._update_dropped_state()
            case GameState.GAME_OVER:
                pass
            case GameState.WIN:
                pass

    def _draw(self) -> None:
        """ General drawing method """
        pyxel.cls(0)

        if self.current_game_state == GameState.WIN:
            pyxel.text(10, pyxel.height - 10, "Game Over! You've completed all stages!", pyxel.COLOR_WHITE, None)
            return
        if self.current_game_state == GameState.READY:
            self._draw_ready_state()

        if self.current_game_state == GameState.GAME_OVER:
            pyxel.text(10, pyxel.height - 10, "Game Over!", pyxel.COLOR_WHITE, None)
            return

        self._draw_game_elements()
        self._draw_ui()
        
BreakoutGame()