import pyxel
from paddle import Paddle


class Reward:
    def __init__(self, x: float, y: float, points: int, falling_accel: float) -> None:
        """ Constructor for Score Object """
        self.x = x
        self.y = y
        self.w = 6
        self.h = 10
        self.accel = falling_accel
        self.speed_y: float = 0.5 # initial speed
        self.P = points

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++

    def collides(self, paddle: Paddle) -> tuple[bool, int]:
        """ Method that deals with all collisions of score objects with game elements """

        if self.y < pyxel.height: # checks if score object is still within the window
            if (
                self.x < paddle.x + paddle.w and  # reward's left edge is to the left of paddle's right edge
                self.x + self.w > paddle.x and             # reward's right edge is to the right of paddle's left edge
                self.y < paddle.y + paddle.h and # reward's top edge is above paddle's bottom edge
                self.y + self.h > paddle.y                # reward's bottom edge is below paddle's top edge
                ): # if the score object collides with the paddle
                return True, self.P  # collision with paddle, points added
            else:
                return False, 0 # didn't hit the bottom, but also didn't hit the paddle 
        
        return True, 0 # hit the bottom so don't add any to the score    
        

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
            u=1,
            v=83,
            w=self.w,
            h=self.h,
            colkey=pyxel.COLOR_PEACH
        )