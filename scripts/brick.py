"""
Module Name: brick.py

Description:
    Contains all the logic pertaining to a "Brick" object used in the game.

Author: Josh Patiño
Date: January 01, 2025
"""

import pyxel
from random import choice


BrickType: dict[int, dict[str, int]] = {
    1: { # book (regular)
        "img": 0,
        "w": 32,
        "h": 16,
        "health": 1,
        "colkey": pyxel.COLOR_LIGHT_BLUE,
    },
    2: { # bacon (sturdy)
        "img": 0,
        "w": 32,
        "h": 16,
        "health": 2,
        "colkey": pyxel.COLOR_LIGHT_BLUE,
    },
    3: { # eggs (very sturdy)
        "img": 0,
        "w": 16,
        "h": 16,
        "health": 3,
        "colkey": pyxel.COLOR_RED,
    },
    4: { # stone slabs (indestructible)
        "img": 0,
        "w": 32,
        "h": 16,
        "health": -1, # meaning it can't be broken
        "colkey": pyxel.COLOR_LIGHT_BLUE,
    },
    5: { # ball maker
        "img": 0,
        "w": 32,
        "h": 16,
        "health": 1,
        "colkey": pyxel.COLOR_LIGHT_BLUE
    }
}

class Brick:
    """

    A brick object used in the game.

    Attributes:
        brick_type (int):                               type of brick (1-5)
        x (float):                                      brick's x-pos
        y (float):                                      brick's y-pos
        w (int):                                        brick's width
        h (int):                                        brick's height
        health (int):                                   brick's durability (-1 for indestructible)
        img (int):                                      image bank for sprite
        colkey (int):                                   color key for transparency
        skins_1 (list[tuple[int, int]]):                containing sprite positions for type 1
        skins_2 (list[tuple[int, int]]):                containing sprite positions for type 2
        skins_3 (list[tuple[int, int]]):                containing sprite positions for type 3
        skins_4 (list[tuple[int, int]]):                containing sprite positions for type 4
        current_skin (tuple[int, int]):                 current (u,v) sprite position
        K (int):                                        no. of score objects in brick

    Methods:
        __init__(self, x: float, y: float, brick_type: int, K: int) -> None:
            Initializes a Brick object with position and type.

            Args:
                x (float):                      x-pos of brick
                y (float):                      y-pos of brick
                brick_type (int):               brick's type
                K (int):                        no. of score objects in brick

        destroy(self) -> None:
            Conveys a message to destroy brick.

        draw(self) -> None:
            Renders the brick sprite.

    """


    def __init__(self, x: float, y: float, brick_type: int, K: int) -> None:
        """ Constructor for brick """
        self.brick_type = brick_type
        self.x = x
        self.y = y
        self.w = BrickType[brick_type]["w"]
        self.h = BrickType[brick_type]["h"]
        self.health = BrickType[self.brick_type]["health"]
        self.img = BrickType[self.brick_type]["img"]
        self.colkey = BrickType[brick_type]["colkey"]
        self.skins_1 = [(16,0), (16,16), (16,32), (16,48), (16,64), (16,80)]        # brick type 1
        self.skins_2 = [(16, 112), (16,96)]                                         # brick type 2 (arranged in reverse)
        self.skins_3 = [(0, 64), (0,48), (0, 32)]                                   # brick type 3 (arranged in reverse)
        self.skins_4 = [(48, 0), (48, 16)]                                          # brick type 4
        self.current_skin: tuple[int, int]                                          # (u, v)
        self.K = K

        match brick_type:
            case 1:
                self.current_skin = choice(self.skins_1)
            case 2:
                self.current_skin = self.skins_2[self.health - 1]                   # uses the first stage of brick type 2
            case 3:
                self.current_skin = self.skins_3[self.health - 1]                   # uses the first stage of brick type 3
            case 4:
                self.current_skin = choice(self.skins_4)                            # random choice
            case 5:
                self.current_skin = 48, 112                                         # (u, v)
            case _:                                                            
                pass                                                                # shouldn't happen

    def destroy(self) -> bool:
        """ Conveys message to destroy brick -> ball -> game """
        return True

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