import pyxel


class Paddle:
    def __init__(self) -> None:
        """ Constructor for paddle """
        self.w: float = 48
        self.h: float = 8
        self.x = pyxel.width // 2 - self.w // 2
        self.y = pyxel.height - 50
        self.mid_sections = 4
        self.sprite_img = 0
        self.sprite_w = 8 
        self.sprite_h = 8
        self.sprite_end_u = 8
        self.sprite_end_v = 0
        self.sprite_mid_u = 0
        self.sprite_mid_v = 8
        self.score = 0 # Just for pyright

    def update(self) -> None:
        """ Move the paddle left and right based on the mouse location """
        self.x = min(pyxel.width - self.w, max(0, pyxel.mouse_x))

    def draw(self) -> None:
        """ Drawing method for paddle """
        pyxel.blt(
            self.x,
            self.y,
            self.sprite_img,
            self.sprite_end_u,
            self.sprite_end_v,
            self.sprite_w,
            self.sprite_h
        )
        for i in range(0, self.mid_sections):
            pyxel.blt(
                self.x + self.sprite_w + (self.sprite_w * i),
                self.y,
                self.sprite_img,
                self.sprite_mid_u,
                self.sprite_mid_v,
                self.sprite_w,
                self.sprite_h
            )

        pyxel.blt(
            self.x + self.sprite_w + self.sprite_w * self.mid_sections,
            self.y,
            self.sprite_img,
            self.sprite_end_u,
            self.sprite_end_v,
            -self.sprite_w,
            -self.sprite_h
        )

    def deflect_force(self, u: float) -> float:
        """ """
        # Return the deflect force of the ball on the paddle
        force: float = (u - (self.x + self.w / 2)) / 10
        return force