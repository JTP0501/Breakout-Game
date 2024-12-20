import pyxel
import enum
import json
from ball import Ball
from paddle import Paddle 
from brick import Brick


class GameState(enum.Enum):
    """ The game states """
    READY = 0
    RUNNING = 1
    DROPPED = 2
    GAME_OVER = 3
    WIN = 4


class BreakoutGame:
    def __init__(self) -> None:
        """ Constructor """
        pyxel.init(width=384, height=300, display_scale=2, title="Breakout Game", fps=60)
        pyxel.load("../assets/resources.pyxres")
        pyxel.mouse(True)

        self.paddle = Paddle()
        self.ball = Ball()
        self._reset_ball()

        self.stages: list[dict[str, list[dict[str, int]]]] = self._load_stages("../assets/stages.json")
        self.current_stage: int = 0
        self.bricks: list[Brick] = []
        self._load_stage(self.current_stage)

        self.current_game_state = GameState.READY
        pyxel.run(self._update, self._draw)
    
    def _load_stages(self, file_path: str) -> list[dict[str, list[dict[str, int]]]]:
        """Load stages from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        return data["stages"]

    def _load_stage(self, stage_index: int) -> None:
        """Load a specific stage."""
        stage = self.stages[stage_index]
        self.bricks = [
            Brick(brick["x"], brick["y"], brick["brick_type"])
            for brick in stage["bricks"]
        ]

    def _next_stage(self) -> None:
        """Move to the next stage."""
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            self._load_stage(self.current_stage)
        else:
            print("Game Over! You've completed all stages!")

    def _reset_ball(self):
        """ """
        self.ball.x = self.paddle.x + self.paddle.w / 2 + 10
        self.ball.y = self.paddle.y - self.ball.r
        self.ball.speed_x = self.paddle.deflect_force(self.ball.x)
        self.ball.speed_y = -2.5
        self.ball.out_of_bounds = False

    def _update(self) -> None:
        """ """
        self._check_input()
        self.paddle.update()
        if self.current_game_state == GameState.READY:
            # Update the ball x-position - it should be stuck to the paddle
            self.ball.x = self.paddle.x + self.paddle.w / 2 + 10

        if self.current_game_state == GameState.RUNNING:
            self.ball.update()
            self._check_collision()

            if not self.bricks: # Level Cleared
                self._next_stage()
                self._reset_ball()
                self.current_game_state = GameState.READY

            if self.ball.out_of_bounds:
                self.current_game_state = GameState.DROPPED
        
    def _check_collision(self) -> None:
        """ """
        # Ball vs Paddle
        collision: bool = self.ball.detect_collision(self.paddle, paddle=True)
        if collision:
            pass
        # Ball vs Bricks
        for i in reversed(range(len(self.bricks))):
            b: Brick = self.bricks[i]
            collision = self.ball.detect_collision(b)
            if collision:
                del self.bricks[i]
                break

    def _check_input(self) -> None:
        """ """
        if self.current_game_state == GameState.READY:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                # Launch the ball and set the game running
                self.current_game_state = GameState.RUNNING
        if self.current_game_state == GameState.DROPPED:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                # Launch the ball and set the game running
                self._reset_ball()
                self.current_game_state = GameState.READY

    def _draw(self) -> None:
        """ """
        pyxel.cls(0)
        self.paddle.draw()

        for brick in self.bricks:
            brick.draw()

        self.ball.draw()
        pyxel.text(10, pyxel.height - 20, str(self.current_game_state), pyxel.COLOR_WHITE, None)


BreakoutGame()


