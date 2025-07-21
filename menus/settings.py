from ursina import *
from ursina.prefabs.slider import ThinSlider
from ursina.prefabs.dropdown_menu import DropdownMenuButton
from ursina.prefabs.button_group import ButtonGroup

import pypresence, json, copy, asyncio

from utils.utils import FakePyPresence, Dropdown, FileManager, FocusView, is_float
from utils.constants import discord_presence_id, settings, settings_start_category
from utils.preload import music_sound

class Settings(FocusView):
    def __init__(self, pypresence_client):
        super().__init__(model='cube', color=color.dark_gray, scale=(1.8, 1.2), z=1)

        self.pypresence_client = pypresence_client
        pypresence_client.update(state='In Settings', details='Modifying Settings', start=pypresence_client.start_time)

        self.data = json.load(open('settings.json'))
        self.edits = {}
        self.category = settings_start_category

        self.ui = [self.main]

        self.category_group = ButtonGroup(tuple(settings.keys()), default=self.category, spacing=(.25, 0, 0))
        self.category_group.on_value_changed = lambda: self.show(self.category_group.value)
        self.category_group.position = (-.6, .4)
        self.ui.append(self.category_group)

        self.weapon_dmg_inputs = {}
        self.weapon_atk_speed_inputs = {}
        self.weapon_img_paths = {}
        self.weapon_img_path_buttons = {}
        self.weapon_remove_buttons = {}

        self.enemy_speed_inputs = {}
        self.enemy_size_inputs = {}
        self.enemy_img_paths = {}
        self.enemy_img_path_buttons = {}
        self.enemy_remove_buttons = {}

        self.back_button = Button('Back', parent=camera.ui, color=color.gray, scale=(.1, .05), position=(-.8, .45), on_click=self.exit)

        self.show(self.category)

        self.ui.append(self.back_button)

        self.detect_focusable_widgets()

    def show(self, category):
        self.clear()
        self.category = category

        if category == "Credits":
            self.credits()
            return
        elif category == "Weapons":
            self.weapons()
            return
        elif category == "Enemies":
            self.enemies()
            return

        y = .2

        for name, info in settings[category].items():
            key, type = info['config_key'], info['type']
            val = self.data.get(key, info.get('default') or info['options'][0])

            self.ui.append(Text(name, parent=camera.ui, position=(-.6, y), scale=1.2))

            if type == 'bool':
                bool_button_group = ButtonGroup(('OFF', 'ON'), default='ON' if val else 'OFF', spacing=(.1, 0, 0))
                bool_button_group.position = (.2, y)
                bool_button_group.on_value_changed = lambda bool_button_group=bool_button_group, n=name: self.update_settings(n, bool_button_group.value == 'ON')
                self.ui.append(bool_button_group)

            elif type == 'slider':
                slider = ThinSlider(min=info['min'], max=info['max'], default=val, dynamic=True)
                slider.position = (.2, y)
                slider.on_value_changed = lambda slider=slider, n=name: self.update_settings(n, int(slider.value))
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

        self.detect_focusable_widgets()

    def directory_selected(self, btn, name, value):
        btn.text = f"Select Directory ({value})"

        self.update_settings(name, value)

    def select_directory(self, btn, name):
        self.dir_file_manager = FileManager(return_folders=True, z=-1)
        self.dir_file_manager.on_submit = lambda value, btn=btn, name=name: self.directory_selected(btn, name, str(value[0]))

    def image_file_selected(self, btn, item_type, name, value):
        btn.text = f"Select File ({value})"
        if item_type == "weapon":
            self.weapon_img_paths[name] = value
        elif item_type == "enemy":
            self.enemy_img_paths[name] = value

    def select_image_file(self, btn, name, item_type):
        self.file_manager = FileManager(z=-1)
        self.file_manager.on_submit = lambda value, btn=btn, name=name: self.image_file_selected(btn, item_type, name, str(value[0]))

    def dropdown_update(self, n, dropdown_menu, btn):
        dropdown_menu.text = btn.text

        self.update_settings(n, btn.text)

    def update_settings(self, name, value):
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
            if isinstance(self.pypresence_client, FakePyPresence): # the user has enabled pypresence_client in the settings in this session.
                start_time = copy.deepcopy(self.pypresence_client.start_time)
                self.pypresence_client.close()
                del self.pypresence_client
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.update(state='In Settings', details='Modifying Settings', start=start_time)
                    self.pypresence_client.start_time = start_time
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = start_time
        else:
            if not isinstance(self.pypresence_client, FakePyPresence):
                start_time = copy.deepcopy(self.pypresence_client.start_time)
                self.pypresence_client.update()
                self.pypresence_client.close()
                del self.pypresence_client
                self.pypresence_client = FakePyPresence()
                self.pypresence_client.start_time = start_time

        if self.data['music']:
            if not music_sound.playing:
                music_sound.play()
                music_sound.loop = True
            music_sound.volume = self.data.get("music_volume", 50) / 100
        else:
            music_sound.stop()

        self.data["weapons"] = self.data.get("weapons", settings["Weapons"]["default"])
        self.data["enemies"] = self.data.get("enemies", settings["Enemies"]["default"])

        if self.category == "Weapons":
            for name in self.data["weapons"]:
                dmg, attack_speed, image = self.weapon_dmg_inputs[name].text, self.weapon_atk_speed_inputs[name].text, self.weapon_img_paths[name]
                self.data["weapons"][name] = {"dmg": float(dmg), "atk_speed": float(attack_speed), "image": image}

        elif self.category == "Enemies":
            for name in self.data["enemies"]:
                speed, size, image = self.enemy_speed_inputs[name].text, self.enemy_size_inputs[name].text, self.enemy_img_paths[name]
                self.data["enemies"][name] = {"speed": float(speed), "size": float(size), "image": image}

        json.dump(self.data, open('settings.json', 'w'), indent=4)

        self.hide()
        self.__init__(self.pypresence_client)

    def add_enemy(self):
        name, speed, size, image = self.new_enemy_name_input.text, self.enemy_speed_inputs["New"].text, self.enemy_size_inputs["New"].text, self.enemy_img_paths["New"]
        self.data["enemies"] = self.data.get("enemies", settings["Enemies"]["default"])
        
        if name in self.data["enemies"] or not name or not speed or not is_float(speed) or not size or not is_float or not image:
            return

        self.data["enemies"][name] = {"speed": float(speed), "size": float(size), "image": image}
        self.clear()
        self.enemies()

    def add_weapon(self):
        name, dmg, atk_speed, image = self.new_weapon_name_input.text, self.weapon_dmg_inputs["New"].text, self.weapon_atk_speed_inputs["New"].text, self.weapon_img_paths["New"]
        self.data["weapons"] = self.data.get("weapons", settings["Weapons"]["default"])
        
        if name in self.data["weapons"] or not name or not dmg or not is_float(dmg) or not atk_speed or not is_float(atk_speed) or not image:
            return
        
        self.data["weapons"][name] = {"dmg": float(dmg), "atk_speed": float(atk_speed), "image": image}
        self.clear()
        self.weapons()

    def remove_enemy(self, name):
        self.data["enemies"] = self.data.get("enemies", settings["Enemies"]["default"])
        del self.data["enemies"][name]
        self.clear()
        self.enemies()

    def remove_weapon(self, name):
        self.data["weapons"] = self.data.get("weapons", settings["Weapons"]["default"])
        del self.data["weapons"][name]
        self.clear()
        self.weapons()

    def enemies(self):
        y = .3

        for enemy_name, enemy_dict in list(self.data.get("enemies", settings["Enemies"]["default"]).items()) + list({"New": {"speed": 0.1, "size": 1.0, "image": None}}.items()):
            speed, size, image = enemy_dict["speed"], enemy_dict["size"], enemy_dict["image"]
            self.enemy_img_paths[enemy_name] = image

            if not image is None:
                self.ui.append(Text(enemy_name, parent=camera.ui, position=(-.8, y), scale=1.2))
            else:
                self.new_enemy_name_input = InputField(default_value="New", parent=camera.ui, position=(-.75, y - .01), scale_x=0.125, scale_y=.05)
                self.ui.append(self.new_enemy_name_input)

            self.ui.append(Text("Speed: ", parent=camera.ui, position=(-.6, y), scale=1.2))
            self.enemy_speed_inputs[enemy_name] = InputField(default_value=str(round(speed, 2)), parent=camera.ui, position=(-.4, y - .01), scale_x=0.125, scale_y=.05)
            self.ui.append(self.enemy_speed_inputs[enemy_name])

            self.ui.append(Text("Size: ", parent=camera.ui, position=(-.3, y), scale=1.2))
            self.enemy_size_inputs[enemy_name] = InputField(default_value=str(round(size, 2)), parent=camera.ui, position=(-.15, y - .01), scale_x=0.125, scale_y=.05)
            self.ui.append(self.enemy_size_inputs[enemy_name])

            self.ui.append(Text("Image Path: ", parent=camera.ui, position=(-.05, y), scale=1.2))
            self.enemy_img_path_buttons[enemy_name] = Button(text=f"Select File ({image})", scale_x=.6, scale_y=0.05, text_size=.5, position=(0.43, y - .01))
            self.enemy_img_path_buttons[enemy_name].on_click = lambda name=enemy_name, btn=self.enemy_img_path_buttons[enemy_name]: self.select_image_file(btn, name, "enemy")
            self.ui.append(self.enemy_img_path_buttons[enemy_name])

            if image is None:
                self.enemy_add_button = Button(text="Add", scale_x=.1, scale_y=0.05, text_size=.7, position=(0.8, y - .01))
                self.enemy_add_button.on_click = lambda: self.add_enemy()
                self.ui.append(self.enemy_add_button)
            else:
                self.enemy_remove_buttons[enemy_name] = Button(text="Remove", scale_x=.1, scale_y=0.05, text_size=.7, position=(0.8, y - .01))
                self.enemy_remove_buttons[enemy_name].on_click = lambda name=enemy_name: self.remove_enemy(name)
                self.ui.append(self.enemy_remove_buttons[enemy_name])                

            y -= 0.08
        
        self.apply_button = Button('Apply', parent=camera.ui, color=color.green, scale=(.15, .08), position=(.6, -.4), on_click=self.apply_changes)
        self.ui.append(self.apply_button)

        self.detect_focusable_widgets()

    def weapons(self):
        y = .3

        for weapon_name, weapon_dict in list(self.data.get("weapons", settings["Weapons"]["default"]).items()) + list({"New": {"dmg": 10, "atk_speed": 0.1, "image": None}}.items()):
            dmg, atk_speed, image = weapon_dict["dmg"], weapon_dict["atk_speed"], weapon_dict["image"]
            self.weapon_img_paths[weapon_name] = image

            if not image is None:
                self.ui.append(Text(weapon_name, parent=camera.ui, position=(-.8, y), scale=1.2))
            else:
                self.new_weapon_name_input = InputField(default_value="New", parent=camera.ui, position=(-.75, y - .01), scale_x=0.125, scale_y=.05)
                self.ui.append(self.new_weapon_name_input)

            self.ui.append(Text("DMG: ", parent=camera.ui, position=(-.6, y), scale=1.2))
            self.weapon_dmg_inputs[weapon_name] = InputField(default_value=str(round(dmg, 2)), parent=camera.ui, position=(-.45, y - .01), scale_x=0.125, scale_y=.05)
            self.ui.append(self.weapon_dmg_inputs[weapon_name])

            self.ui.append(Text("Attack Speed: ", parent=camera.ui, position=(-.35, y), scale=1.2))
            self.weapon_atk_speed_inputs[weapon_name] = InputField(default_value=str(round(atk_speed, 2)), parent=camera.ui, position=(-0.075, y - .01), scale_x=0.125, scale_y=.05)
            self.ui.append(self.weapon_atk_speed_inputs[weapon_name])

            self.ui.append(Text("Image Path: ", parent=camera.ui, position=(0.025, y), scale=1.2))
            self.weapon_img_path_buttons[weapon_name] = Button(text=f"Select File ({image})", scale_x=.5, scale_y=0.05, text_size=.5, position=(0.475, y - .01))
            self.weapon_img_path_buttons[weapon_name].on_click = lambda name=weapon_name, btn=self.weapon_img_path_buttons[weapon_name]: self.select_image_file(btn, name, "weapon")
            self.ui.append(self.weapon_img_path_buttons[weapon_name])

            if image is None:
                self.weapon_add_button = Button(text="Add", scale_x=.1, scale_y=0.05, text_size=.7, position=(0.8, y - .01))
                self.weapon_add_button.on_click = lambda: self.add_weapon()
                self.ui.append(self.weapon_add_button)
            else:
                self.weapon_remove_buttons[weapon_name] = Button(text="Remove", scale_x=.1, scale_y=0.05, text_size=.7, position=(0.8, y - .01))
                self.weapon_remove_buttons[weapon_name].on_click = lambda name=weapon_name: self.remove_weapon(name)
                self.ui.append(self.weapon_remove_buttons[weapon_name])

            y -= 0.08 

        self.apply_button = Button('Apply', parent=camera.ui, color=color.green, scale=(.15, .08), position=(.6, -.4), on_click=self.apply_changes)
        self.ui.append(self.apply_button)

        self.detect_focusable_widgets()

    def clear(self):
        for e in list(self.ui):
            if e not in (self.main, self.back_button, self.category_group):
                destroy(e)
                self.ui.remove(e)

        self.detect_focusable_widgets()

    def exit(self):
        self.hide()
        from menus.main import Main
        Main(pypresence_client=self.pypresence_client)

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

        self.detect_focusable_widgets()