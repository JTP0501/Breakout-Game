import pyxel
from ball import Ball
from paddle import Paddle 


class BreakoutGame:
    def __init__(self) -> None:
        pyxel.init(width=384, height=300, display_scale=2, title="Breakout Game", fps=60)
        pyxel.load("../assets/resources.pyxres")
        self.paddle = Paddle()
        self.ball = Ball(x=100, y=100)
        pyxel.run(self.update, self.draw)
    
    def update(self):
        self.ball.update()

    def draw(self):
        pyxel.cls(0)
        self.paddle.draw()
        self.ball.draw()


BreakoutGame()


