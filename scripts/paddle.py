import pyxel


class Paddle:
    def __init__(self) -> None:
        """ Constructor for paddle """
        self.w: float = 80  # width of the paddle (based on sprite)
        self.h: float = 9   # height of the paddle (based on sprite)
        self.x: float = pyxel.width // 2 - self.w // 2  # starts in the middle of the screen
        self.y: float = pyxel.height - 40  # positions it near the bottom
        self.sprite_img : int = 1  # The img bank where the paddle is located
        self.sprite_u : int = 0 # the (u,v) of the paddle in the img (u=0, v=7)    
        self.sprite_v: int = 7
        self.speed: float = 4 # speed of paddle 
        self.score: int = 0       # Just for pyright (not used here)

        self.mark_w: int = 12
        self.mark_h: int = 16
        self.mark_u: int = 2
        self.mark_v: int = 16

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++

    def deflect_force(self, u: float) -> float:
        """ Calculate the deflect force of the ball on the paddle """
        force: float = (u - (self.x + self.w / 2)) / 10  # Force based on hit position
        return force

# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def update(self) -> None:
        """ Moves the paddle left and right based on the mouse location with constant velocity """
        target_x: float = pyxel.mouse_x - self.w / 2 # centers the paddle on the mouse

        if self.x < target_x:
            self.x += min(self.speed, target_x - self.x)  # moves right, but not beyond the target
        elif self.x > target_x:
            self.x -= min(self.speed, self.x - target_x)  # moves left, but not beyond the target
        
        # keeps the paddle within screen bounds
        self.x = max(0, min(self.x, pyxel.width - self.w))

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

         # draws a vertical line as the mouse x-coordinate marker
        pyxel.blt(x=pyxel.mouse_x - self.mark_w,
                y=pyxel.height - self.mark_h,
                img=self.sprite_img,
                u=self.mark_u,
                v=self.mark_v,
                w=self.mark_w,
                h=self.mark_h,
                colkey=pyxel.COLOR_DARK_BLUE)

        # displays the mouse x-coordinate as text
        #pyxel.text(5, pyxel.height - 10, f"Mouse X: {pyxel.mouse_x}", pyxel.COLOR_WHITE, None)
