import pyxel

from paddle import Paddle
from brick import Brick
from math import ceil


class Ball:
    def __init__(self) -> None:
        """ Constructor for ball """
        self.x: float = 0
        self.y: float = 0
        self.speed_x: float = 2.0
        self.speed_y: float = -1.5 
        self.r: int = 2
        self.out_of_bounds: bool = False
        self.trail: list[tuple[float, float]] = []
        self.trail_margin: float = 3
        self.shimmer_counter: int = 0
        self.shimmer_rate: int = 3

    def draw(self) -> None:
        """ Drawing method for ball and its shimmering trail """
        
        # Draw the shimmering trail
        self.shimmer_counter = (self.shimmer_counter + 1) % self.shimmer_rate
        if self.shimmer_counter == 0: # "Shimmer" for certain frames only
            for _, (trail_x, trail_y) in enumerate(self.trail):
                # Make the trail shimmer with a uniform color and fading brightness
                pyxel.pset(
                    pyxel.rndi(ceil(trail_x - self.trail_margin), 
                              ceil(trail_x + self.trail_margin)),
                    pyxel.rndi(int(trail_y), 
                              ceil(trail_y + self.trail_margin)),
                    col=pyxel.COLOR_YELLOW
                )
        # Draw the ball itself
        pyxel.circ(self.x, self.y, self.r, col=pyxel.COLOR_WHITE)  # Glowing ball

    def update(self) -> None:
        """ Move the ball, then check if it should bounce """

        # Store the current position in the trail
        self.trail.append((self.x, self.y))

        # Limit trail length (keep only the last 10 positions)
        if len(self.trail) > 10:
            self.trail.pop(0)

        self.x += self.speed_x
        self.y += self.speed_y

        if self.x + self.r >= pyxel.width:
            self.speed_x = -self.speed_x
        elif self.y - self.r <= 0:
            self.speed_y = -self.speed_y
        elif self.x - self.r <= 0:
            self.speed_x = -self.speed_x
        elif self.y - self.r >= pyxel.height:
            self.out_of_bounds = True
    
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

            if (
                sub_ball_x + self.r >= obj.x
                and sub_ball_x - self.r <= obj.x + obj.w
                and sub_ball_y + self.r >= obj.y
                and sub_ball_y - self.r <= obj.y + obj.h
            ):
                # Deflect the ball
                if paddle:
                    self.speed_x = obj.deflect_force(self.x)
                    self.speed_y = -self.speed_y
                elif sub_ball_x + self.r >= obj.x > sub_ball_x - self.r:
                    # Ball hit left side of brick
                    self.x = obj.x - self.r
                    self.speed_x = -self.speed_x

                elif sub_ball_x - self.r <= obj.x + obj.w < sub_ball_x + self.r:
                    # Ball hit right side of brick
                    self.x = obj.x + obj.w + self.r
                    self.speed_x = -self.speed_x

                elif sub_ball_y + self.r >= obj.y > sub_ball_y - self.r:
                    self.y = obj.y - self.r
                    self.speed_y = -self.speed_y

                elif sub_ball_y - self.r <= obj.y + obj.h < sub_ball_y + self.r:
                    self.y = obj.y + obj.h + self.r
                    self.speed_y = -self.speed_y
                
                score = obj.score
                return True, score # Collision detected
        return False, score # No collision detected