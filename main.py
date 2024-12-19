import pyxel

class BreakoutGame:
    def __init__(self) -> None:
        pyxel.init(width=384, height=300, display_scale=3, title="Breakout Game", fps=60)
        pyxel.run(self.update, self.draw)
    
    def update(self):
        pass

    def draw(self):
        pass


