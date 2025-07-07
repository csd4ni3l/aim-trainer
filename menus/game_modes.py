import json

from utils.constants import game_modes
from utils.utils import FocusView

from ursina import *

class GameModeSelector(FocusView):
    def __init__(self, rpc):
        super().__init__(model='cube', color=color.dark_gray, scale=(1.8, 1.2), z=1)

        self.rpc = rpc
        rpc.update(state='In Game Mode Selector', details='Selecting Game Mode Selector', start=rpc.start_time)

        self.back_button = Button('Back', parent=camera.ui, color=color.gray, scale=(.1, .05), position=(-.8, .45), on_click=self.exit)
        self.title_label = Text(text="Select a mode to play.", position=(-0.4, 0.425), scale=3)

        y = 0.2

        for game_mode in game_modes:
            button = Button(text=game_mode, scale_x=1, scale_y=0.15, text_size=2, position=(0, y), on_click=lambda game_mode=game_mode: self.play(game_mode))
            self.ui.append(button)
            y -= 0.16
    
        self.ui.extend([self.back_button, self.title_label, self.main])

        self.detect_focusable_widgets()

    def play(self, game_mode):
        self.hide()
        from game.game import Game
        Game(self.rpc, game_mode.lower())

    def exit(self):
        self.hide()
        from menus.main import Main
        Main(pypresence_client=self.rpc)