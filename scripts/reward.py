import pyxel
from paddle import Paddle


class Reward:
    def __init__(self, x: float, y: float, points: int, falling_accel: float) -> None:
        """ Constructor for Score Object """
        self.x = x
        self.y = y
        self.w = 8
        self.h = 10
        self.accel = falling_accel
        self.speed_y: float = pyxel.rndf(0.5,0.75) # initial speed
        self.P = points

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++
    
    def collides(self, paddle: Paddle) -> tuple[str | None, int]:
        """
        Method that deals with all collisions of score objects with game elements.
        """

        if self.y < pyxel.height:  # still within the screen
            if (
                self.x < paddle.x + paddle.w and  # reward's left edge is to the left of paddle's right edge
                self.x + self.w > paddle.x and   # reward's right edge is to the right of paddle's left edge
                self.y < paddle.y + paddle.h and # reward's top edge is above paddle's bottom edge
                self.y + self.h > paddle.y       # reward's bottom edge is below paddle's top edge
            ):
                return "paddle", self.P  # collision with paddle
            else:
                return None, 0  # no collision with paddle

        return "bottom", 0  # hit the bottom of the screen

        

# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def _move_object(self) -> None:
        """ This method moves the score object """
        self.speed_y += self.accel
        self.y += self.speed_y # moves the object down 

    def update(self) -> None:
        """ General Update Method for Score Object """
        self._move_object()

# +++++++++++++++++++++++++++++++++ DRAW METHODS +++++++++++++++++++++++++++++++++

    def draw(self) -> None:
        """ General Draw Method for Score Object """
        # draws the score object on the screen
        pyxel.blt(
            x=self.x,
            y=self.y,
            img=0,
            u=0,
            v=83,
            w=self.w,
            h=self.h,
            colkey=pyxel.COLOR_PEACH
        )