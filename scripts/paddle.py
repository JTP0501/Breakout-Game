import pyxel


class Paddle:
    def __init__(self) -> None:
        """ Constructor for paddle """
        self.w: float = 80  # width of the paddle (based on sprite)
        self.h: float = 9   # height of the paddle (based on sprite)
        self.x = pyxel.width // 2 - self.w // 2  # starts in the middle of the screen
        self.y = pyxel.height - 40  # positions it near the bottom
        self.sprite_img = 1  # The img bank where the paddle is located
        self.sprite_u = 0 # the (u,v) of the paddle in the img (u=0, v=7)    
        self.sprite_v = 7    
        self.score = 0       # Just for pyright (not used here)

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++

    def deflect_force(self, u: float) -> float:
        """ Calculate the deflect force of the ball on the paddle """
        force: float = (u - (self.x + self.w / 2)) / 10  # Force based on hit position
        return force

# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def update(self) -> None:
        """ Moves the paddle left and right based on the mouse location """
        self.x = min(pyxel.width - self.w, max(0, pyxel.mouse_x))

# +++++++++++++++++++++++++++++++++ DRAW METHODS +++++++++++++++++++++++++++++++++

    def draw(self) -> None:
        """ Draw method for paddle """
        # draws the full paddle as one image
        pyxel.blt(
            x=self.x,  # x-position
            y=self.y,  # y-position
            img=self.sprite_img,  # img bank
            u=self.sprite_u,  # u-position in sprite sheet
            v=self.sprite_v,  # v-position in sprite sheet
            w=self.w,  # width of the sprite
            h=self.h,   # height of the sprite
            colkey=pyxel.COLOR_YELLOW # keyed out color 
        )
