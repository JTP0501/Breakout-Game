import pyxel

from random import choice

BrickType: dict[int, dict[str, int]] = {
    1: { # book (regular)
        "img": 0,
        "w": 32,
        "h": 16,
        "health": 1,
        "colkey": 6,
    },
    2: { # bacon (sturdy)
        "img": 0,
        "w": 32,
        "h": 16,
        "health": 2,
        "colkey": 6,
    },
    3: { # eggs (very sturdy)
        "img": 0,
        "w": 16,
        "h": 16,
        "health": 3,
        "colkey": 8,
    },
    4: { # stone slabs (indestructible)
        "img": 0,
        "w": 32,
        "h": 16,
        "health": -1, # meaning it can't be broken
        "colkey": 6,
    }
}

class Brick:
    def __init__(self, x: float, y: float, brick_type: int) -> None:
        """ Constructor for brick """
        self.brick_type = brick_type
        self.x = x
        self.y = y
        self.w = BrickType[brick_type]["w"]
        self.h = BrickType[brick_type]["h"]
        self.health = BrickType[self.brick_type]["health"]
        self.img = BrickType[self.brick_type]["img"]
        self.colkey = BrickType[brick_type]["colkey"]
        self.skins_1 = [(16,0), (16,16), (16,32), (16,48), (16,64), (16,80)] # brick type 1
        self.skins_2 = [(16, 112), (16,96)] # brick type 2 (arranged in reverse)
        self.skins_3 = [(0, 64), (0,48), (0, 32)] # brick type 3
        self.skins_4 = [(48, 0), (48, 16)] # brick type 4
        self.current_skin: tuple[int, int]
        match brick_type:
            case 1:
                self.current_skin = choice(self.skins_1)
            case 2:
                self.current_skin = self.skins_2[self.health - 1] # use the first stage of brick type 2
            case 3:
                self.current_skin = self.skins_3[self.health - 1] # use the first stage of brick type 3
            case 4:
                self.current_skin = choice(self.skins_4) # random choice
            case _:
                # shouldn't happen
                pass
    
    def hit(self) -> bool:
        """ Method for discerning response to being hit """
        self.health -= 1
        if self.health > 0:
            # only two cases, if brick type is 2 or 3
            if self.brick_type == 2: # 2
                self.current_skin = self.skins_2[self.health - 1]
            else: # 3
                self.current_skin = self.skins_3[self.health - 1]
        return self.health == 0 # True if it should be deleted

    def draw(self) -> None:
        """ Drawing method for brick """
        pyxel.blt(
            self.x,
            self.y,
            self.img,
            self.current_skin[0],
            self.current_skin[1],
            self.w,
            self.h,
            self.colkey
        )