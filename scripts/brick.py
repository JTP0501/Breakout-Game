import pyxel

from random import choice

BrickType: dict[int, dict[str, int]] = {
    1: {
        "img": 0,
        "u": 0,
        "v": 0,
        "w": 32,
        "h": 16,
        "colkey": 6,
    },
    2: {
        "img": 0,
        "u": 17,
        "v": 17,
        "w": 30,
        "h": 14,
        "colkey": 0,
    },
    3: {
        "img": 0,
        "u": 17,
        "v": 33,
        "w": 30,
        "h": 14,
        "colkey": 0,
    },
    4: {
        "img": 0,
        "u": 17,
        "v": 1,
        "w": 30,
        "h": 14,
        "colkey": 0,
    }, 
}

class Brick:
    def __init__(self, x: float, y: float, brick_type: int) -> None:
        """ Constructor for brick """
        self.x = x
        self.y = y
        self.brick_type = brick_type
        self.img = BrickType[self.brick_type]["img"]
        self.w = BrickType[brick_type]["w"]
        self.h = BrickType[brick_type]["h"]
        self.skins_1 = [(16,0), (16,16), (16,32), (16,48), (16,64), (16,80)]
        if brick_type == 1:
            self.u, self.v = choice(self.skins_1)
        else:
            self.u = BrickType[brick_type]["u"]
            self.v = BrickType[brick_type]["v"]
        self.colkey = BrickType[brick_type]["colkey"]
    
    def draw(self) -> None:
        """ Drawing method for brick """
        pyxel.blt(
            self.x,
            self.y,
            self.img,
            self.u,
            self.v,
            self.w,
            self.h,
            self.colkey
        )