import json
from utils.constants import game_modes
from ursina import *

class GameModeSelector:
    def __init__(self, rpc):
        self.rpc = rpc
        rpc.update(state='In Game Mode Selector', details='Selecting Game Mode Selector', start=rpc.start_time)

        self.data = json.load(open('settings.json'))
        
        self.main = Entity(parent=camera.ui, model='cube', color=color.dark_gray, scale=(1.8, 1.2), z=1)
        self.back_button = Button('Back', parent=camera.ui, color=color.gray, scale=(.1, .05), position=(-.8, .45), on_click=self.exit)
        self.title_label = Text(text="Select a mode to play.", position=(-0.4, 0.35), scale=3)

        self.ui = [self.main, self.back_button, self.title_label]

        y = 0.1

        for game_mode in game_modes:
            button = Button(text=game_mode, scale_x=1, scale_y=0.2, text_size=2, position=(0, y), on_click=lambda game_mode=game_mode: self.play(game_mode))
            self.ui.append(button)
            y -= 0.21

    def play(self, game_mode):
        self.hide()
        from game.game import Game
        Game(self.rpc, game_mode.lower())

    def hide(self):
        for e in self.ui:
            destroy(e)
        self.ui.clear()

    def exit(self):
        self.hide()
        from menus.main import Main
        Main(pypresence_client=self.rpc)