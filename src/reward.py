"""
Module Name: reward.py

Description:
     Contains all the logic pertaining to the "Reward" objects used in the game.
    These are score objects that fall from broken bricks.

Author: Josh Patiño
Date: January 01, 2025
"""

import pyxel
from src.paddle import Paddle
from random import choice


class Reward:
    """
    A falling reward object that can be collected by the paddle.

    Attributes:
        x (float):                                  reward's x-position
        y (float):                                  reward's y-position
        w (int):                                    width of reward sprite
        h (int):                                    height of reward sprite
        accel (float):                              vertical falling acceleration
        speed_y (float):                            initial falling speed
        P (int):                                    score value when collected
        powerup_type (str):                         the type of powerup (if applicable)
        sprites (dict[str, tuple[int, int]]):       the powerup type and its respective (u, v) values for its sprite
    
    Methods:
        __init__(self, x: float, y: float, points: int, falling_accel: float, X: int, powerup_type: str ="") -> None:
            Initializes reward at given position.

            Args:
                x (float):                          x-pos of reward
                y (float):                          y-pos of reward
                points (int):                       point contribution of reward
                falling_accel (float):              the "gravity" of falling score object
                X (int):                            the percent chance of a score object being a power up
                powerup_type (str):                 the type of powerup, empty if not a powerup

        collides(self, paddle: Paddle) -> tuple[str | None, int]:
            Handles collision of score object with paddle and/or bottom of window.

            Args:
                paddle (Paddle):                    the paddle collided with

        _move_object(self) -> None:
            Handles the movement of the score object.

        update(self) -> None:
            Updates score object position.

        draw(self) -> None:
            Renders reward with the appropriate sprite.

    """
    
    def __init__(self, x: float, y: float, points: int, falling_accel: float, X: int, powerup_type: str = "") -> None:
        """ Constructor for Score Object """
        self.x = x
        self.y = y
        self.w = 8
        self.h = 10
        self.accel = falling_accel
        self.speed_y: float = pyxel.rndf(0.5,0.75)              # initial speed
        self.P = points
        self.powerup_type = powerup_type

                                                                # determines if this reward is a power-up
        self.is_powerup = pyxel.rndi(1, 100) <= X
        self.powerup_type = None

        if self.is_powerup:
            self.powerup_type = choice(["life_up", "antigravity", "paddle_speed", "double_points"])

                                                                # defines the powerup types
        self.sprites = {
            "life_up": (0, 115),                                # (u, v, w, h) coordinates for sprite
            "antigravity": (8, 83),
            "paddle_speed": (8, 99),
            "double_points": (0, 99)
        }

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++
    
    def collides(self, paddle: Paddle) -> tuple[str | None, int]:
        """ Method that deals with all collisions of score objects with game elements """

        if self.y < pyxel.height:                               # still within the screen
            if (
                self.x < paddle.x + paddle.w and                # reward's left edge is to the left of paddle's right edge
                self.x + self.w > paddle.x and                  # reward's right edge is to the right of paddle's left edge
                self.y < paddle.y + paddle.h and                # reward's top edge is above paddle's bottom edge
                self.y + self.h > paddle.y                      # reward's bottom edge is below paddle's top edge
            ):
                return "paddle", self.P                         # collision with paddle
            else:
                return None, 0                                  # no collision with paddle

        return "bottom", 0                                      # hit the bottom of the screen

# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def _move_object(self) -> None:
        """ This method moves the score object """
        self.speed_y += self.accel
        self.y += self.speed_y                                  # moves the object down 

    def update(self) -> None:
        """ General Update Method for Score Object """
        self._move_object()

# +++++++++++++++++++++++++++++++++ DRAW METHODS +++++++++++++++++++++++++++++++++

    def draw(self) -> None:
        """ General Draw Method for Score Object """
                                                                # draws the score object on the screen
        if self.is_powerup and self.powerup_type in self.sprites:
            u, v = self.sprites[self.powerup_type]
        else:
            u, v = 0, 83
        pyxel.blt(
            x=self.x,
            y=self.y,
            img=0,
            u=u,
            v=v,
            w=self.w,
            h=self.h,
            colkey=pyxel.COLOR_PEACH
        )