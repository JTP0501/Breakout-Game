import pyxel

from paddle import Paddle
from brick import Brick
from math import ceil


class Ball:
    def __init__(self) -> None:
        """ Constructor for ball """
        # General
        self.x: float = 0 # ball's x-position
        self.y: float = 0 # ball's y-position
        self.speed_x: float = 2.0 # initial x-speed of ball
        self.speed_y: float = -1.5 # initial y-speed of ball
        self.r: int = 4 # ball's radius (based on the sprite)
        self.img: int = 0 # image bank of sprite
        self.sprite_u: int = 0 # sprite's (u,v) position in img, start with default (u=0, v=16)
        self.sprite_v: int = 16 
        self.out_of_bounds: bool = False # tracks if sprite is still within bounds
        
        # Trail 
        self.trail: list[tuple[float, float]] = [] # list of past positions of ball for trail
        self.trail_margin: float = 3 # how far the randomized particle will be at most
        self.shimmer_rate: int = 3 # the rate at which the trail "shimmers"

        # Sprite
        self.sprite_change_interval: int = 300 # 300 frames (5 seconds)
        self.last_sprite_change: int = 0 # tracks frames for sprite change logic

# +++++++++++++++++++++++++++++++++ HELPER METHODS +++++++++++++++++++++++++++++++++

    def clear_trails(self) -> None:
            """ Clear all ball trails """
            self.trail.clear() # clears the trail list

    def detect_collision(self, obj: Paddle | Brick, paddle: bool = False) -> tuple[bool, int]:
        """ """
        score: int = 0
        # Calculate the no. of sub-steps for the contiguous collision detection
        num_steps: int = ceil(max(abs(self.speed_x), abs(self.speed_y)))
        
        if num_steps == 0:
            return False, score # Ball is not moving
        
        # Calculate the step size for each sub-segment
        step_size: float = 1.0 / num_steps

        # Check for collisions along the sub-segments
        for step in range(1, num_steps + 1):
            t = step * step_size # Interpolation factor between the start and end of the sub-segment
            sub_ball_x: float = self.x + t * self.speed_x   
            sub_ball_y: float = self.y + t * self.speed_y

            # ball's bounding box at the sub-step position
            ball_left = sub_ball_x
            ball_right = sub_ball_x + 2 * self.r 
            ball_top = sub_ball_y
            ball_bottom = sub_ball_y + 2 * self.r

            # object's bounding box
            obj_left = obj.x
            obj_right = obj.x + obj.w
            obj_top = obj.y
            obj_bottom = obj.y + obj.h

            # Check for overlap
            if (
                ball_right >= obj_left
                and ball_left <= obj_right
                and ball_bottom >= obj_top
                and ball_top <= obj_bottom
            ):
                # Deflect the ball
                if paddle:  # Ball vs Paddle
                    # Handle collision from top
                    if ball_bottom >= obj_top > ball_top:
                        self.y = obj_top - 2 * self.r
                        self.speed_y = -abs(self.speed_y)  # Bounce up

                    # Handle collision from left
                    elif ball_right >= obj_left > ball_left:
                        self.x = obj_left - 2 * self.r
                        self.speed_x = -abs(self.speed_x)

                    # Handle collision from right
                    elif ball_left <= obj_right < ball_right:
                        self.x = obj_right
                        self.speed_x = abs(self.speed_x)

                    # Handle collision from bottom
                    elif ball_top <= obj_bottom < ball_bottom:
                        self.y = obj_bottom
                        self.speed_y = abs(self.speed_y)  # Bounce down

                    # Adjust horizontal speed based on paddle contact
                    self.speed_x = obj.deflect_force(self.x + self.r)

                else: # Ball vs Brick
                    if ball_right >= obj_left > ball_left:
                        # Ball hit the left side of the brick
                        self.x = obj_left - 2 * self.r
                        self.speed_x = -self.speed_x

                    elif ball_left <= obj_right < ball_right:
                        # Ball hit the right side of the brick
                        self.x = obj_right
                        self.speed_x = -self.speed_x

                    elif ball_bottom >= obj_top > ball_top:
                        # Ball hit the top of the brick
                        self.y = obj_top - 2 * self.r
                        self.speed_y = -self.speed_y

                    elif ball_top <= obj_bottom < ball_bottom:
                        # Ball hit the bottom of the brick
                        self.y = obj_bottom
                        self.speed_y = -self.speed_y

                score = obj.score
                return True, score  # Collision detected
        return False, score  # No collision detected

# +++++++++++++++++++++++++++++++++ UPDATE METHODS +++++++++++++++++++++++++++++++++

    def _update_trail(self) -> None:
        """ Update the ball's trail """
        self.trail.append((self.x, self.y)) # stores the curr position in the trail
        if len(self.trail) > 10:
            self.trail.pop(0)
    
    def _move_ball(self) -> None:
        """ Move the ball based on its speed """
        self.x += self.speed_x
        self.y += self.speed_y

    def _check_bounds(self) -> None:
        # Check collisions with window boundaries
        if self.x <= 0:  # Left wall
            self.x = 0
            self.speed_x = -self.speed_x
        elif self.x + 2 * self.r >= pyxel.width:  # Right wall
            self.x = pyxel.width - 2 * self.r
            self.speed_x = -self.speed_x

        if self.y <= 0:  # Top wall
            self.y = 0
            self.speed_y = -self.speed_y
        elif self.y + 2 * self.r >= pyxel.height:  # Bottom (out of bounds)
            self.y = pyxel.height - 2 * self.r
            self.out_of_bounds = True
    
    def _update_sprite(self) -> None:
        """ Update the ball's sprite every few seconds """

        # changes the sprite every 300 frames (5 seconds)
        if pyxel.frame_count - self.last_sprite_change >= self.sprite_change_interval:
            self.last_sprite_change = pyxel.frame_count
            self._cycle_sprite()
    
    def _cycle_sprite(self) -> None:
        """ Cycle through the ball's sprite """
        if self.sprite_u == 0 and self.sprite_v == 16:
            self.sprite_u, self.sprite_v = 8, 16
        elif self.sprite_u == 8 and self.sprite_v == 16:
            self.sprite_u, self.sprite_v = 0, 24
        elif self.sprite_u == 0 and self.sprite_v == 24:
            self.sprite_u, self.sprite_v = 8, 24
        else:
            self.sprite_u, self.sprite_v = 0, 16

    def update(self) -> None:
        """ Move the ball, then check if it should bounce """
        self._update_trail()
        self._move_ball()
        self._check_bounds()
        self._update_sprite()

# +++++++++++++++++++++++++++++++++ DRAW METHODS +++++++++++++++++++++++++++++++++

    def _draw_trail(self) -> None:
        """ Draw the shimmering trail effect """
        if pyxel.frame_count % self.shimmer_rate == 0:
            for trail_x, trail_y in self.trail:
                pyxel.pset(
                    pyxel.rndi(ceil(trail_x - self.trail_margin), ceil(trail_x + self.trail_margin)),
                    pyxel.rndi(int(trail_y), ceil(trail_y + self.trail_margin)),
                    pyxel.COLOR_ORANGE
                )

    def _draw_ball(self) -> None:
        """ Draw the ball itself with its sprite """
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