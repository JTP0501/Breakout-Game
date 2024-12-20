import pyxel
import enum
from ball import Ball
from paddle import Paddle 


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
        self.current_game_state = GameState.READY
        pyxel.run(self._update, self._draw)
    
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
            if self.ball.out_of_bounds:
                self.current_game_state = GameState.DROPPED
        
    def _check_collision(self) -> None:
        """ """
        # Ball vs Paddle
        collision: bool = self.ball.detect_collision(self.paddle, paddle=True)
        if collision:
            pass

    def _check_input(self) -> None:
        """ """
        if self.current_game_state == GameState.READY:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) or pyxel.btnp(pyxel.KEY_SPACE):
                # Launch the ball and set the game running
                self.current_game_state = GameState.RUNNING

    def _draw(self) -> None:
        """ """
        pyxel.cls(0)
        self.paddle.draw()
        self.ball.draw()


BreakoutGame()


