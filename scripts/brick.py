#import pyxel


class Brick:
    def __init__(self) -> None:
        """ """
        self.x: float = 0
        self.y: float = 0
        self.w: float = 0
        self.h: float = 0
    
    def deflect_force(self, u: float) -> float:
        """ """
        # Return the deflect force of the ball on the brick
        force: float = (u - (self.x + self.w / 2)) / 10
        return force

""" Temp """