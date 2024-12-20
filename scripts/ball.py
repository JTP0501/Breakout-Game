import pyxel


class Ball:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.speed_x: float = 2.0
        self.speed_y: float = -1.5 
        self.r: int = 2
        self.out_of_bounds: bool = False

    def draw(self) -> None:
        pyxel.circ(self.x, self.y, self.r, col=pyxel.COLOR_WHITE)
    
    def update(self) -> None:
        """ Move the ball, then check if it should bounce """
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x + self.r >= pyxel.width:
            self.speed_x = -self.speed_x
        elif self.y - self.r <= 0:
            self.speed_y = -self.speed_y
        elif self.x - self.r <= 0:
            self.speed_x = -self.speed_x
        elif self.y - self.r >= pyxel.height:
            self.out_of_bounds = True