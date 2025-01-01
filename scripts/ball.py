"""
Module Name: ball.py

Description:
    Contains all the logic pertaining to a "Ball" object used in the game.

Author: Josh Patiño
Date: January 01, 2025
"""

import pyxel
from paddle import Paddle
from brick import Brick
from math import ceil, radians, cos, sin
from random import choice


class Ball:
    """ 
    
    A ball object used in the game.

    Attributes:
        x (float):                              ball's x-pos
        y (float):                              ball's y-pos
        direction_x (int):                      ball's horizontal direction
        direction_y (int):                      ball's vertical direction
        speed_x (float):                        ball's horizontal speed
        speed_y (float):                        ball's vertical speed
        gravity (float):                        "gravity" felt by the ball
        VELOCITY_INCREASE (float):              amount the speed of the ball increases
        MAX_SPEED (float):                      caps the speed of the ball
        r (int):                                radius of the ball
        trail (list[tuple[float, float]]):      contains past positions of the ball
        trail_margin (float):                   trail deviation
        trail_length (float):                   how many positions are kept track of for the trail
        img (int):                              img bank of the sprite
        sprite_u (int):                         u-pos in resources
        sprite_v (int):                         v-pos in resources
        sprite_change_interval (int):           no. of frames before changing sprite
        last_sprite_change (int):               tracks frames for sprite change
        destroy_brick (bool):                   tells game to destroy brick or not
        out_of_bounds (bool):                   tracks if ball is out of bounds
    
    Methods:
        __init__(self, gravity: float) -> None:
            Initializes a Ball object with given gravity value.
            
            Args:
                gravity (float):                    gravity inputted from the main module
        
        _handle_collisions(self, obj: Paddle | Brick, contact: float, is_x: bool, is_upper: bool) -> None:
            Manages response to collision with object.

            Args:
                obj (Paddle | Brick):               the object collided with (a paddle or brick)
                contact (float):                    "axis" of contact        
                is_x (bool):                        True if it hits the top or bottom, and False if it hits the left or right
                is_upper (bool):                    True if it hits the top or left, False if it hits the bottom or right

        _detect_collision(self, elem: Paddle | Brick) -> bool:
            Checks for and handles collisions with other game objects.
            
            Args:
                elem (Paddle | Brick):              the object being inspected for collision with ball

            Returns:
                (bool)
                True = Collision
                False = No Collision

        _check_bounds(self) -> None:
            Handles collision with window bounds.
        
        _update_trail(self) -> None:
            Handles the tracking of previous positions and 
        
        clear_trails(self) -> None:
            Clears all stored trail positions.

        _move_ball(self) -> None:
            Moves the ball.
        
        _update_sprite(self) -> None:
            Updates the ball's sprite.    
        
        _cycle_sprite(self) -> None:
            Changes the sprite in a sequential loop.
        
        update(self) -> None:
            Moves the ball and updates the sprite and trail, and also deals with collisions with the window.

        _draw_trail(self) -> None:
            Draws the trail.
        
        _draw_ball(self) -> None:
            Draws the ball with its current sprite.

        draw(self) -> None:
            Draws the ball with its trail.

            
    """
    def __init__(self, gravity: float) -> None:
        """ Constructor for ball """
        # position and movement
        self.x: float = 0                                   
        self.y: float = 0                                   
        self.direction_x: int = 1                           # 1 for right, -1 for left
        self.direction_y: int = -1                          # 1 for down, -1 for up
        # physics of the ball
        self.speed_x: float
        self.speed_y: float
        self.gravity: float = gravity
        self.VELOCITY_INCREASE: float = 0.25                # constants
        self.MAX_SPEED: float = 2.5
        self.r: int = 4 
        
        # ball trail
        self.trail: list[tuple[float, float]] = []          # list of past positions of ball for trail
        self.trail_margin: float = 3                        # how far the randomized particle will be at most
        self.trail_length: int = 10

        # appearance of ball
        self.img: int = 0 
        self.sprite_u: int = 0                              # sprite's (u,v) position
        self.sprite_v: int = 16 
        self.sprite_change_interval: int = 300              # 5 seconds
        self.last_sprite_change: int = 0                    # tracks frames for sprite change logic     
        
        self.destroy_brick: bool = False                    # msg for game to destroy brick with no health hit by ball
        self.out_of_bounds: bool = False                    # tracks if sprite is still within bounds

# +++++++++++++++++++++++++++++++++ COLLISION METHODS +++++++++++++++++++++++++++++++++
    
    def _handle_collisions(self, obj: Paddle | Brick, contact: float, is_x: bool, is_upper: bool) -> None:
        """ Handles collision deflection based on contact point """
                                                            # uses the horizontal center if x related else vertical center
        obj_center = obj.x + obj.w / 2 if is_x else obj.y + obj.h / 2 
        contact_offset = contact - obj_center
        max_offset = obj.w / 2 if is_x else obj.h / 2       # max offset from center to edge
        relative_offset = contact_offset / max_offset       # normalizes to [-1, 1]

        angle = 90 if is_x else 180                         # defaults to straight-up deflection (initially)

        scale = abs(relative_offset)
        
                                                            # collision logic
        if is_x:                                            # top/bottom side of brick
            if is_upper:                                    # top side
                if scale < 0.05:                            # hits the horizontal center
                    angle = 90                              # directly upward
                else:
                    if self.direction_x == 1:               # ball coming from the left
                        angle = 90 + scale * (20 - 90)  
                    else:                                   # ball coming from the right
                        angle = 90 - scale * (20 - 90)  
            else:                                           # bottom side
                if isinstance(obj, Paddle):
                    angle = 270 
                else:
                    if scale < 0.05:                        # hits the horizontal center
                        angle = 270                         # directly downward
                    else:
                        if self.direction_x == 1:           # ball coming from the left
                            angle = 270 + scale * (340 - 270)  
                        else:                               # ball coming from the right
                            angle = 270 - scale * (340 - 270)  
        else:                                               # left/right side of brick
            if is_upper:                                    # left side
                if scale < 0.05:                            # hits the vertical center
                    angle = 180                             # directly left
                else:
                    if self.direction_y == -1:              # ball coming from below
                        angle = 180 - scale * (180 - 110)
                    else:                                   # ball coming from above
                        angle = 180 + scale * (250 - 180)  
            else:                                           # right side
                if scale < 0.05:                            # hits the vertical center
                    angle = 360                             # directly right
                else:
                    if self.direction_y == -1:              # ball coming from below
                        angle = (360 + scale * abs(310 - 360)) % 360 
                    else:                                   # ball coming from above
                        angle = 360 - scale * abs(250 - 360)
 
        angle_radians = radians(angle)

        curr_magnitude = (self.speed_x**2 + self.speed_y**2)**0.5
        self.speed_x = curr_magnitude * cos(angle_radians)
        self.speed_y = -curr_magnitude * sin(angle_radians) # negative to align with upward motion

        if angle in [90, 270]:                              # straight up or down
                                                            # adds slight variation to `x` speed to ensure ball is always in play
            self.speed_x += (-0.1 if self.direction_x == -1 else 0.1)

    def detect_collision(self, elem: Paddle | Brick) -> bool:
        """ Detects collisions with the paddle or bricks """

                                                            # ball's next position after applying speed
        next_x = self.x + self.speed_x
        next_y = self.y + self.speed_y

                                                            # ball's bounding box at the interpolated position
        ball_left = next_x
        ball_right = next_x + 2 * self.r
        ball_top = next_y
        ball_bottom = next_y + 2 * self.r

                                                            # elem's bounding box
        obj_left = elem.x
        obj_right = elem.x + elem.w
        obj_top = elem.y
        obj_bottom = elem.y + elem.h

                                                            # checks for overlap
        if (ball_right >= obj_left 
        and ball_left <= obj_right 
        and ball_bottom >= obj_top 
        and ball_top <= obj_bottom):
            
                                                            # the point at which the ball hits the elem
            
            contact_x = max(obj_left, min(ball_right, obj_right)) 
            contact_y = max(obj_top, min(ball_bottom, obj_bottom))

            overlap_x = min(abs(ball_right - obj_left), abs(ball_left - obj_right))
            overlap_y = min(abs(ball_bottom - obj_top), abs(ball_top - obj_bottom))

            # Note: is_upper: True: [top, left], False: [bottom, right]

                                                            # determines collision sides
            if overlap_y < overlap_x:                       # vertical collision
                if ball_bottom >= obj_top > ball_top:       # top of brick
                    self.y -= overlap_y * 0.9
                    self._handle_collisions(obj=elem, contact=contact_x, is_x=True, is_upper=True)
                elif ball_top <= obj_bottom < ball_bottom:  # bottom of brick
                    self.y += overlap_y * 0.9
                    self._handle_collisions(obj=elem, contact=contact_x, is_x=True, is_upper=False)
            else:                                           # horizontal collision
                if ball_left <= obj_right < ball_right:     # right side of brick
                    self.x += overlap_x * 0.9
                    self._handle_collisions(obj=elem, contact=contact_y, is_x=False, is_upper=False)
                elif ball_right >= obj_left > ball_left:    # left side of brick
                    self.x -= overlap_x * 0.9
                    self._handle_collisions(obj=elem, contact=contact_y, is_x=False, is_upper=True)

            if isinstance(elem, Brick):
                                                            # applies health reduction logic
                if elem.health > 0:
                    elem.health -= 1                        # reduces health once per collision
                    if elem.health == 0:
                        self.destroy_brick = elem.destroy() # calls a method to tell the game to destroy the brick when health reaches 0
                    elif elem.health > 0:                   # if brick has multiple stages
                        match elem.brick_type:
                            case 2:
                                elem.current_skin = elem.skins_2[elem.health - 1]
                            case 3:
                                elem.current_skin = elem.skins_3[elem.health - 1]
                            case _:
                                pass

                                                            # applies speed cap and proportional increase
            curr_magnitude = (self.speed_x**2 + self.speed_y**2)**0.5
            new_magnitude = min(curr_magnitude + self.VELOCITY_INCREASE, self.MAX_SPEED)
            speed_ratio = new_magnitude / curr_magnitude
            self.speed_x *= speed_ratio
            self.speed_y *= speed_ratio

            return True                                     # collision detected

        return False                                        # no collision detected

    def _check_bounds(self) -> None:
        """ Checks collisions with window boundaries """
        if self.x <= 0:                                     # left wall
            self.x = 0
            self.speed_x = -self.speed_x
        elif self.x + 2 * self.r >= pyxel.width:            # right wall
            self.x = pyxel.width - 2 * self.r
            self.speed_x = -self.speed_x

        if self.y <= 0:                                     # top wall
            self.y = 0
            self.speed_y = -self.speed_y
        elif self.y + 2 * self.r >= pyxel.height:           # bottom (out of bounds)
            self.y = pyxel.height - 2 * self.r
            self.out_of_bounds = True
    
# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def _update_trail(self) -> None:
        """ Updates the ball's trail """
        self.trail.append((self.x, self.y))                 # stores the current position in the trail
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

    def clear_trails(self) -> None:
        """ Clears all ball trails """
        self.trail.clear()                                  # clears the trail list
            
    def _move_ball(self) -> None:
        """ Moves the ball based on its speed """
        self.speed_y += self.gravity                        # applies gravity
        self.speed_y = min(self.speed_y, 5)                 # caps the downward speed
        self.x += self.speed_x
        self.y += self.speed_y

                                                            # updates directions
        self.direction_x = 1 if self.speed_x > 0 else -1
        self.direction_y = 1 if self.speed_y > 0 else -1
    
    def _update_sprite(self) -> None:
        """ Updates the ball's sprite every few seconds """

                                                            # changes the sprite every 300 frames (5 seconds)
        if pyxel.frame_count - self.last_sprite_change >= self.sprite_change_interval:
            self.last_sprite_change = pyxel.frame_count
            self._cycle_sprite()
    
    def _cycle_sprite(self) -> None:
        """ Cycles through the ball's sprite """
        if self.sprite_u == 0 and self.sprite_v == 16:
            self.sprite_u, self.sprite_v = 8, 16
        elif self.sprite_u == 8 and self.sprite_v == 16:
            self.sprite_u, self.sprite_v = 0, 24
        elif self.sprite_u == 0 and self.sprite_v == 24:
            self.sprite_u, self.sprite_v = 8, 24
        else:
            self.sprite_u, self.sprite_v = 0, 16

    def update(self) -> None:
        """ Moves the ball, then check if it should bounce """
        self._update_trail()
        self._move_ball()
        self._check_bounds()
        self._update_sprite()

# +++++++++++++++++++++++++++++++++ DRAW METHODS +++++++++++++++++++++++++++++++++

    def _draw_trail(self) -> None:
        """ Draws the shimmering trail effect """
        for trail_x, trail_y in self.trail:
            pyxel.circb(
                x=pyxel.rndi(ceil(trail_x - self.trail_margin), ceil(trail_x + self.trail_margin)),
                y=pyxel.rndi(int(trail_y), ceil(trail_y + self.trail_margin)),
                r=0.5,
                col=choice([pyxel.COLOR_ORANGE, pyxel.COLOR_RED, pyxel.COLOR_YELLOW])
            )

    def _draw_ball(self) -> None:
        """ Draws the ball itself with its sprite """
        pyxel.blt(
            x=self.x,
            y=self.y,
            img=self.img,
            u=self.sprite_u,
            v=self.sprite_v,
            w=self.r * 2,
            h=self.r * 2,
            colkey=pyxel.COLOR_LIGHT_BLUE
        )

    def draw(self) -> None:
        """ Drawing method for ball and its shimmering trail """
        self._draw_trail()
        self._draw_ball()