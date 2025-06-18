from ursina import *
from ursina.prefabs.slider import ThinSlider
from ursina.prefabs.dropdown_menu import DropdownMenuButton
from ursina.prefabs.button_group import ButtonGroup

import pypresence, json, copy
from utils.utils import FakePyPresence, Dropdown, FileManager
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

        self.dmg_inputs = {}
        self.atk_speed_inputs = {}
        self.weapon_img_paths = {}
        self.img_path_buttons = {}
        self.save_buttons = {}

        self.show(self.category)

    def show(self, category):
        self.clear()
        self.category = category

        if category == "Credits":
            self.credits()
            return
        elif category == "Weapons":
            self.weapons()
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

            elif type == "option":
                menu_buttons = []
                for opt in info['options']:
                    menu_button = DropdownMenuButton(opt)
                    menu_buttons.append(menu_button)

                dropdown_menu = Dropdown(val, buttons=tuple(menu_buttons))
                
                for menu_button in menu_buttons:
                    menu_button.on_click = lambda dropdown_menu=dropdown_menu, btn=menu_button, n=name: self.dropdown_update(n, dropdown_menu, btn)

                dropdown_menu.position = (.2, y)
                self.ui.append(dropdown_menu)

            elif type == "directory_select":
                directory_select_button = Button(text=f"Select Directory ({val})", scale_x=1.1, scale_y=0.1, text_size=.7, position = (.33, y))
                directory_select_button.on_click = lambda btn=directory_select_button, name=name: self.select_directory(btn, name)

                self.ui.append(directory_select_button)

            y -= .08

        self.apply_button = Button('Apply', parent=camera.ui, color=color.green, scale=(.15, .08), position=(.6, -.4), on_click=self.apply_changes)
        self.ui.append(self.apply_button)

    def directory_selected(self, btn, name, value):
        btn.text = f"Select Directory ({value})"

        self.update(name, value)

    def select_directory(self, btn, name):
        self.dir_file_manager = FileManager(return_folders=True, z=-1)
        self.dir_file_manager.on_submit = lambda value, btn=btn, name=name: self.directory_selected(btn, name, str(value[0]))

    def image_file_selected(self, btn, name, value):
        btn.text = f"Select File ({value})"
        self.weapon_img_paths[name] = value

    def select_image_file(self, btn, name):
        self.file_manager = FileManager(z=-1)
        self.file_manager.on_submit = lambda value, btn=btn, name=name: self.image_file_selected(btn, name, str(value[0]))

    def dropdown_update(self, n, dropdown_menu, btn):
        dropdown_menu.text = btn.text

        self.update(n, btn.text)

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
            font_size = 2.3
        elif window.size.x >= 2560:
            font_size = 1.8
        elif window.size.x >= 1920:
            font_size = 1.5
        elif window.size.x >= 1440:
            font_size = 1.2
        else:
            font_size = 1.0

        self.credits_label = Text(text=text, parent=camera.ui, position=(0, 0), origin=(0, 0), scale=font_size, color=color.white)
        self.credits_label.type = 'credits_text'
        self.ui.append(self.credits_label)

    def save_weapon(self, name):
        dmg, attack_speed, image = self.dmg_inputs[name].text, self.atk_speed_inputs[name].text, self.weapon_img_paths[name]

        self.edits["weapons"] = self.edits.get("weapons", settings["Weapons"]["default"])
        self.edits["weapons"][name] = {"dmg": float(dmg), "atk_speed": float(attack_speed), "image": image}

        self.apply_changes()

    def weapons(self):
        y = .2

        for weapon_name, weapon_dict in self.data.get("weapons", settings["Weapons"]["default"]).items():
            dmg, atk_speed, image = weapon_dict["dmg"], weapon_dict["atk_speed"], weapon_dict["image"]

            self.ui.append(Text(weapon_name, parent=camera.ui, position=(-.8, y), scale=1.2))

            self.ui.append(Text("DMG: ", parent=camera.ui, position=(-.6, y), scale=1.2))
            self.dmg_inputs[weapon_name] = InputField(default_value=str(round(dmg, 2)), parent=camera.ui, position=(-.45, y - .01), scale_x=0.125, scale_y=.05)
            self.ui.append(self.dmg_inputs[weapon_name])

            self.ui.append(Text("Attack Speed: ", parent=camera.ui, position=(-.35, y), scale=1.2))
            self.atk_speed_inputs[weapon_name] = InputField(default_value=str(round(atk_speed, 2)), parent=camera.ui, position=(-0.075, y - .01), scale_x=0.125, scale_y=.05)
            self.ui.append(self.atk_speed_inputs[weapon_name])

            self.ui.append(Text("Image Path: ", parent=camera.ui, position=(0.05, y), scale=1.2))
            self.img_path_buttons[weapon_name] = Button(text=f"Select File ({image})", scale_x=.3, scale_y=0.05, text_size=.5, position=(0.4, y - .01))
            self.img_path_buttons[weapon_name].on_click = lambda name=weapon_name, btn=self.img_path_buttons[weapon_name]: self.select_image_file(btn, name)
            self.ui.append(self.img_path_buttons[weapon_name])

            self.save_buttons[weapon_name] = Button(text="Save", scale_x=.1, scale_y=0.05, text_size=.7, position=(0.7, y - .01))
            self.save_buttons[weapon_name].on_click = lambda name=weapon_name: self.save_weapon(name)
            self.ui.append(self.save_buttons[weapon_name])

            y -= 0.08 