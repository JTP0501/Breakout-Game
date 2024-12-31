import pyxel

class Sounds:

    # 60 fps
    GAME_OVER_SOUND_TIMEOUT = 120 # 2 seconds
    WIN_SOUND_TIMEOUT = 120 # 2 seconds

    def __init__(self) -> None:
        """ Constructor """
        # channel 1 for other sounds
        self.game_over_framestamp = 0
        self.win_framestamp = 0
        self.game_over_played = False  # flag to check if sound is played
        self.win_played = False # flag to check if sound is played

    def play_ball_hit_sound(self) -> None:
        """ Plays a sound when the ball hits a game element (paddle/bricks)"""
        pyxel.play(1, 3)

    def play_reward_sound(self) -> None:
        """ Plays a sound for capturing a reward with the paddle """
        pyxel.play(1, 4)

    def play_dropped_sound(self) -> None:
        """ Plays a sound for the dropped screen """
        pyxel.play(1, 2)

    def play_launch_sound(self) -> None:
        """ Plays a sound when the ball is launched """
        pyxel.play(1,7) 

    def play_clicked_button_sound(self) -> None:
        """ PLays a sound when a button is clicked """
        pyxel.play(1,8)

    def play_win_sound(self) -> None:
        """ Plays sound on win screen """
        if self.win_played:
            return  # Exit if sound has already been played
        
        current_frame = pyxel.frame_count
        if current_frame - self.win_framestamp >= self.WIN_SOUND_TIMEOUT:
            self.win_played = True  # Set the flag to true
            self.win_framestamp_framestamp = current_frame
            pyxel.play(1, 6)

    def play_game_over_sound(self) -> None:
        """ Plays sound on game over screen """

        if self.game_over_played:
            return  # Exit if sound has already been played
        
        current_frame = pyxel.frame_count
        if current_frame - self.game_over_framestamp >= self.GAME_OVER_SOUND_TIMEOUT:
            self.game_over_played = True  # Set the flag to true
            self.game_over_framestamp = current_frame
            pyxel.play(1, 5)