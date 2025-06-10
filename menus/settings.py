from ursina import *
from ursina.prefabs.slider import ThinSlider
from ursina.prefabs.dropdown_menu import DropdownMenu, DropdownMenuButton
from ursina.prefabs.button_group import ButtonGroup
import pypresence, json, copy
from utils.utils import FakePyPresence
from utils.constants import discord_presence_id, settings, settings_start_category
from utils.preload import music_sound

class Settings:
    def __init__(self, rpc):
        self.rpc = rpc
        rpc.update(state='In Settings', details='Modifying Settings', start=rpc.start_time)

        self.data = json.load(open('settings.json'))
        self.edits = {}
        self.category = settings_start_category
        self.ui = []

        self.main = Entity(parent=camera.ui, model='cube', color=color.dark_gray, scale=(1.8, 1.2), z=1)

        self.back = Button('Back', parent=camera.ui, color=color.gray, scale=(.1, .05), position=(-.8, .45), on_click=self.exit)

        self.category_group = ButtonGroup(tuple(settings.keys()), default=self.category, spacing=(.25, 0, 0))
        self.category_group.on_value_changed = lambda: self.show(self.category_group.value)
        self.category_group.position = (-.6, .4)

        self.ui += [self.main, self.back, self.category_group]

        self.show(self.category)

    def show(self, category):
        self.clear()
        self.category = category

        if category == "Credits":
            self.credits()
            return

        y = .2

        for name, info in settings[category].items():
            key, type = info['config_key'], info['type']
            val = self.data.get(key, info.get('default') or info['options'][0])

            self.ui.append(Text(name, parent=camera.ui, position=(-.6, y), scale=1.2))

            if type == 'bool':
                bool_button_group = ButtonGroup(('OFF', 'ON'), default='ON' if val else 'OFF', spacing=(.1, 0, 0))
                bool_button_group.position = (.2, y)
                bool_button_group.on_value_changed = lambda bool_button_group=bool_button_group, n=name: self.update(n, bool_button_group.value == 'ON')
                self.ui.append(bool_button_group)

            elif type == 'slider':
                slider = ThinSlider(text=name, min=info['min'], max=info['max'], default=val, dynamic=True)
                slider.position = (.2, y)
                slider.on_value_changed = lambda slider=slider, n=name: self.update(n, int(slider.value))
                self.ui.append(slider)

            else:
                items = []
                for opt in info['options']:
                    b = DropdownMenuButton(opt)
                    b.on_click = lambda btn, n=name: self.update(n, btn.text)
                    items.append(b)
                dm = DropdownMenu(val, buttons=tuple(items))
                dm.position = (.2, y)
                self.ui.append(dm)

            y -= .08

        self.apply_button = Button('Apply', parent=camera.ui, color=color.green, scale=(.15, .08), position=(.6, -.4), on_click=self.apply_changes)
        self.ui.append(self.apply_button)

    def update(self, name, value):
        self.edits[settings[self.category][name]['config_key']] = value

    def apply_changes(self):
        self.data.update(self.edits)

        if self.data['window_mode'] == 'Fullscreen':
            window.fullscreen = True
        else:
            window.fullscreen = False
            w, h = map(int, self.data['resolution'].split('x'))
            window.size = Vec2(w, h)

        window.vsync = self.data['vsync']

        if self.data['discord_rpc']:
            if isinstance(self.rpc, FakePyPresence):
                start = copy.deepcopy(self.rpc.start_time)
                self.rpc.close()
                self.rpc = pypresence.Presence(discord_presence_id)
                self.rpc.connect()
                self.rpc.update(state='In Settings', details='Modifying Settings', start=start)
                self.rpc.start_time = start
        else:
            if not isinstance(self.rpc, FakePyPresence):
                start = copy.deepcopy(self.rpc.start_time)
                self.rpc.close()
                self.rpc = FakePyPresence()
                self.rpc.start_time = start

        if self.data['music']:
            if not music_sound.playing:
                music_sound.play()
                music_sound.loop = True
            music_sound.volume = self.data.get("music_volume", 50) / 100
        else:
            music_sound.stop()

        json.dump(self.data, open('settings.json', 'w'), indent=4)
        self.hide()
        self.__init__(self.rpc)

    def clear(self):
        for e in list(self.ui):
            if e not in (self.main, self.back, self.category_group):
                destroy(e)
                self.ui.remove(e)

    def hide(self):
        for e in self.ui:
            destroy(e)
        self.ui.clear()

    def exit(self):
        self.hide()
        from menus.main import Main
        Main(pypresence_client=self.rpc)

    def credits(self):
        if hasattr(self, 'apply_button'):
            destroy(self.apply_button)

        if hasattr(self, 'credits_label'):
            destroy(self.credits_label)

        for e in list(self.ui):
            if hasattr(e, 'type') and e.type == 'credits_text':
                destroy(e)
                self.ui.remove(e)

        with open('CREDITS', 'r') as file:
            text = file.read()

        if window.size.x >= 3840:
            font_size = 2.4
        elif window.size.x >= 2560:
            font_size = 1.9
        elif window.size.x >= 1920:
            font_size = 1.6
        elif window.size.x >= 1440:
            font_size = 1.3
        else:
            font_size = 1.1

        self.credits_label = Text(text=text, parent=camera.ui, position=(0, 0), origin=(0, 0), scale=font_size, color=color.white)
        self.credits_label.type = 'credits_text'
        self.ui.append(self.credits_label)
