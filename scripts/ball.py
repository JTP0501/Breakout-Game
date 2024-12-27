import pyxel
from paddle import Paddle
from brick import Brick
from math import ceil, radians, cos, sin
from random import choice


class Ball:
    def __init__(self, gravity: float) -> None:
        """ Constructor for ball """
        # position and movement
        self.x: float = 0 # ball's x-position
        self.y: float = 0 # ball's y-position
        self.direction_x: int = 1  # 1 for right, -1 for left
        self.direction_y: int = -1  # 1 for down, -1 for up

        # physics of the ball
        self.speed_x: float
        self.speed_y: float
        self.gravity: float = gravity
        self.VELOCITY_INCREASE: float = 0.25
        self.MAX_SPEED: float = 3
        self.r: int = 4 # ball's radius (based on the sprite)
        
        # ball trail
        self.trail: list[tuple[float, float]] = [] # list of past positions of ball for trail
        self.trail_margin: float = 3 # how far the randomized particle will be at most
        self.shimmer_rate: int = 3 # the rate at which the trail "shimmers"
        self.trail_length: int = 10

        # appearance of ball
        self.img: int = 0 # image bank of sprite
        self.sprite_u: int = 0 # sprite's (u,v) position in img, start with default (u=0, v=16)
        self.sprite_v: int = 16 
        self.sprite_change_interval: int = 300 # 300 frames (5 seconds)
        self.last_sprite_change: int = 0 # tracks frames for sprite change logic     
        
        self.out_of_bounds: bool = False # tracks if sprite is still within bounds

# +++++++++++++++++++++++++++++++++ COLLISION METHODS +++++++++++++++++++++++++++++++++
    
    def _handle_collisions(self, obj: Paddle | Brick, contact: float, is_x: bool, is_upper: bool, is_paddle: bool) -> None:
        """ Handles collision deflection based on contact point and object type """
        
        obj_center = obj.x + obj.w / 2 if is_x else obj.y + obj.h / 2 # uses the horizontal center if x related else vertical center
        contact_offset = contact - obj_center
        max_offset = obj.w / 2 if is_x else obj.h / 2  # max offset from center to edge
        relative_offset = contact_offset / max_offset  # normalizes to [-1, 1]

        angle = 90 if is_x else 180  # defaults to straight-up deflection

        scale = abs(relative_offset)
        if is_paddle:  # paddle collision logic
            if is_x:  # top/bottom side of paddle
                if is_upper: # top side
                    if scale < 0.05: # hits the horizontal center
                        angle = 90  # directly upward
                    else:
                        if self.direction_x == 1: # coming from the left
                            angle = 90 + scale * (10 - 90)  
                        else: # coming from the right
                            angle = 90 - scale * (10 - 90) 
                else: # bottom side
                    angle = 270 # deflect downward 
            else:  # left/right side of paddle
                if is_upper:  # left side
                    if scale < 0.05:  # hits the vertical center
                        angle = 180  # directly left
                    else:
                        if self.direction_y == -1:  # ball coming from above
                            angle = 180 + scale * (260 - 180)  
                        else:  # ball coming from below
                            angle = 180 - scale * (180 - 100)
                else: # right side
                    if scale < 0.05:  # hits the vertical center
                        angle = 360  # directly right
                    else:
                        if self.direction_y == -1:  # ball coming from above
                            angle = 360 - scale * abs(260 - 360)
                        else:  # ball coming from below
                            angle = 0 + scale * (80 - 0)
        else:  # brick collision logic
            if is_x:  # top/bottom side of brick
                if is_upper:  # top side
                    if scale < 0.05:  # hits the horizontal center
                        angle = 90  # directly upward
                    else:
                        if self.direction_x == 1:  # ball coming from the left
                            angle = 90 + scale * (10 - 90)  
                        else:  # ball coming from the right
                            angle = 90 - scale * (10 - 90)  
                else:  # bottom side
                    if scale < 0.05:  # hits the horizontal center
                        angle = 270  # directly downward
                    else:
                        if self.direction_x == 1:  # ball coming from the left
                            angle = 270 + scale * (350 - 270)  
                        else:  # ball coming from the right
                            angle = 270 - scale * (350 - 270)  
            else:  # left/right side of brick
                if is_upper:  # left side
                    if scale < 0.05:  # hits the vertical center
                        angle = 180  # directly left
                    else:
                        if self.direction_y == -1:  # ball coming from above
                            angle = 180 + scale * (260 - 180)  
                        else:  # ball coming from below
                            angle = 180 - scale * (180 - 100)
                else: # right side
                    if scale < 0.05:  # hits the vertical center
                        angle = 360  # directly right
                    else:
                        if self.direction_y == -1:  # ball coming from above
                            angle = 360 - scale * abs(260 - 360)
                        else:  # ball coming from below
                            angle = 360 - scale * abs(260 - 360) 

        angle_radians = radians(angle)
        curr_magnitude = (self.speed_x**2 + self.speed_y**2)**0.5
        self.speed_x = curr_magnitude * cos(angle_radians)
        self.speed_y = -curr_magnitude * sin(angle_radians)  # negative to align with upward motion


    def detect_collision(self, obj: Paddle | Brick, is_paddle: bool = False) -> bool:
        """ Detects collisions with the paddle or bricks """

        # calculates number of sub-steps for continuous collision detection
        num_steps = ceil(max(abs(self.speed_x), abs(self.speed_y)))

        if num_steps == 0:
            return False  # ball is not moving
        
        step_size = 1.0 / num_steps

        for step in range(1, num_steps + 1):
            t = step * step_size  # interpolation factor for sub-steps
            sub_ball_x = self.x + t * self.speed_x
            sub_ball_y = self.y + t * self.speed_y

            # ball's bounding box at the interpolated position
            ball_left = sub_ball_x
            ball_right = sub_ball_x + 2 * self.r
            ball_top = sub_ball_y
            ball_bottom = sub_ball_y + 2 * self.r

            # object's bounding box
            obj_left = obj.x
            obj_right = obj.x + obj.w
            obj_top = obj.y
            obj_bottom = obj.y + obj.h

            # checks for overlap
            if (ball_right >= obj_left 
            and ball_left <= obj_right 
            and ball_bottom >= obj_top 
            and ball_top <= obj_bottom):

                contact_x = max(obj_left, min(ball_right, obj_right))
                contact_y = max(obj_top, min(ball_bottom, obj_bottom))

                # is_upper: True: [top, left], False: [bottom, right]

                if is_paddle:
                    # determine collision side for paddle
                    if ball_bottom >= obj_top > ball_top:  # top of paddle
                        self._handle_collisions(obj, contact_x, is_x=True, is_upper=True, is_paddle=True)
                    elif ball_top <= obj_bottom < ball_bottom:  # bottom of paddle
                        self._handle_collisions(obj, contact_x, is_x=True, is_upper=False, is_paddle=True)
                    elif ball_left <= obj_right < ball_right:  # right side of paddle
                        self._handle_collisions(obj, contact_y, is_x=False, is_upper=False, is_paddle=False)
                    elif ball_right >= obj_left > ball_left:  # left side of paddle
                        self._handle_collisions(obj, contact_x, is_x=False, is_upper=True, is_paddle=True)
                else:
                    # determine collision side for bricks
                    if ball_bottom >= obj_top > ball_top:  # top of brick
                        self._handle_collisions(obj, contact_x, is_x=True, is_upper=True, is_paddle=False)
                    elif ball_top <= obj_bottom < ball_bottom:  # bottom of brick
                        self._handle_collisions(obj, contact_x, is_x=True, is_upper=False, is_paddle=False)
                    elif ball_left <= obj_right < ball_right:  # right side of brick
                        self._handle_collisions(obj, contact_y, is_x=False, is_upper=False, is_paddle=False)
                    elif ball_right >= obj_left > ball_left:  # left side of brick
                        self._handle_collisions(obj, contact_y, is_x=False, is_upper=True,is_paddle=False)

                # applies speed cap and proportional increase
                curr_magnitude = (self.speed_x**2 + self.speed_y**2)**0.5
                new_magnitude = min(curr_magnitude + self.VELOCITY_INCREASE, self.MAX_SPEED)
                speed_ratio = new_magnitude / curr_magnitude
                self.speed_x *= speed_ratio
                self.speed_y *= speed_ratio

                return True  # collision detected
        return False # no collision detected
    
# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def _update_trail(self) -> None:
        """ Updates the ball's trail """
        self.trail.append((self.x, self.y)) # stores the current position in the trail
        if len(self.trail) > 10:
            self.trail.pop(0)

    def clear_trails(self) -> None:
        """ Clears all ball trails """
        self.trail.clear() # clears the trail list
            
    def _move_ball(self) -> None:
        """ Moves the ball based on its speed """
        self.speed_y += self.gravity  # apply gravity
        self.speed_y = min(self.speed_y, 5)  # cap the downward speed
        self.x += self.speed_x
        self.y += self.speed_y

        # updates directions
        self.direction_x = 1 if self.speed_x > 0 else -1
        self.direction_y = 1 if self.speed_y > 0 else -1

    def _check_bounds(self) -> None:
        # Checks collisions with window boundaries
        if self.x <= 0:  # left wall
            self.x = 0
            self.speed_x = -self.speed_x
        elif self.x + 2 * self.r >= pyxel.width:  # right wall
            self.x = pyxel.width - 2 * self.r
            self.speed_x = -self.speed_x

        if self.y <= 0:  # top wall
            self.y = 0
            self.speed_y = -self.speed_y
        elif self.y + 2 * self.r >= pyxel.height:  # bottom (out of bounds)
            self.y = pyxel.height - 2 * self.r
            self.out_of_bounds = True
    
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
        if pyxel.frame_count % self.shimmer_rate == 0:
            for trail_x, trail_y in self.trail:
                pyxel.pset(
                    pyxel.rndi(ceil(trail_x - self.trail_margin), ceil(trail_x + self.trail_margin)),
                    pyxel.rndi(int(trail_y), ceil(trail_y + self.trail_margin)),
                    choice([pyxel.COLOR_ORANGE, pyxel.COLOR_RED, pyxel.COLOR_YELLOW])
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