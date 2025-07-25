from ursina import *

import pypresence, asyncio, json, copy

from utils.utils import FakePyPresence, MenuButton, FocusView
from utils.constants import discord_presence_id

class Main(FocusView):
    def __init__(self, pypresence_client=None) -> None:
        super().__init__(y=.15)

        self.pypresence_client = pypresence_client

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        if self.settings_dict.get('discord_rpc', True):
            if self.pypresence_client == None: # Game has started
                try:
                    asyncio.get_event_loop()
                except:
                    asyncio.set_event_loop(asyncio.new_event_loop())
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.start_time = time.time()
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = time.time()

            elif isinstance(self.pypresence_client, FakePyPresence): # the user has enabled RPC in the settings in this session.
                # get start time from old object
                start_time = copy.deepcopy(self.pypresence_client.start_time)
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.start_time = start_time
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = start_time

        else: # game has started, but the user has disabled RPC in the settings.
            self.pypresence_client = FakePyPresence()
            self.pypresence_client.start_time = time.time()

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.high_score = json.load(file)["high_score"]
        else:
            self.high_score = 0

        self.pypresence_client.update(state='In Main Menu', details='In Main Menu')

        button_spacing = .075 * 1.25

        self.title_label = Text("Aim Trainer", parent=self.main, y=-0.01 * button_spacing, scale=3, x=-.2)
        self.high_score_label = Text(f"High Score: {self.high_score}", parent=self.main, scale=1.25, y=-1 * button_spacing, x=-.12)
        
        self.play_button = MenuButton('Play', on_click=Func(self.play), parent=self.main, y=-2 * button_spacing)
        self.settings_button = MenuButton('Settings', on_click=Func(self.settings), parent=self.main, y=-3 * button_spacing)
        self.quit_button = MenuButton('Quit', on_click=Sequence(Wait(.01), Func(application.quit)), parent=self.main, y=-4 * button_spacing)

        self.ui = [self.title_label, self.high_score_label, self.play_button, self.settings_button, self.quit_button]

        self.detect_focusable_widgets()

    def play(self):
        self.hide()
        from menus.game_modes import GameModeSelector
        GameModeSelector(self.pypresence_client)

    def settings(self):
        self.hide()
        from menus.settings import Settings
        Settings(self.pypresence_client)