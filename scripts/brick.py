import pyxel

BrickType: dict[int, dict[str, int]] = {
    1: {
        "img": 0,
        "u": 16,
        "v": 0,
        "w": 32,
        "h": 8,
        "score": 1
    },
    2: {
        "img": 0,
        "u": 16,
        "v": 8,
        "w": 32,
        "h": 8,
        "score": 3
    },
    3: {
        "img": 0,
        "u": 16,
        "v": 16,
        "w": 32,
        "h": 8,
        "score": 5
    },
    4: {
        "img": 0,
        "u": 16,
        "v": 24,
        "w": 32,
        "h": 8,
        "score": 7
    }, 
}

class Brick:
    def __init__(self, x: float, y: float, brick_type: int) -> None:
        """ """
        self.x = x
        self.y = y
        self.brick_type = brick_type
        self.w = BrickType[brick_type]["w"]
        self.h = BrickType[brick_type]["h"]
        self.score = BrickType[brick_type]["score"]
    
    def draw(self) -> None:
        pyxel.blt(
            self.x,
            self.y,
            BrickType[self.brick_type]["img"],
            BrickType[self.brick_type]["u"],
            BrickType[self.brick_type]["v"],
            BrickType[self.brick_type]["w"],
            BrickType[self.brick_type]["h"]
        )

    def deflect_force(self, u: float) -> float:
        """ """
        # Return the deflect force of the ball on the brick
        force: float = (u - (self.x + self.w / 2)) / 10
        return force

""" Temp """