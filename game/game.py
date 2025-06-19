from game.inventory import Inventory
from game.player import Player
from game.enemy import Enemy

from utils.constants import min_enemy_y, max_enemy_y, enemies

from ursina import *
from ursina.shaders import lit_with_shadows_shader

from pathlib import Path

import os, json

class Game():
    def __init__(self, pypresence_client) -> None:
        self.pypresence_client = pypresence_client

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.high_score = json.load(file)["high_score"]
        else:
            self.high_score = 0

        pypresence_client.update(state='Training Aim', details=f'Hits: 0/0 Accuracy: 0%')

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        self.enemy_types = self.settings_dict.get("enemies", enemies)

        self.ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4), shader=lit_with_shadows_shader)

        self.info_label = Text("Score: 0 Hits: 0/0 Accuracy: 0%", parent=camera.ui, position=(-0.1, 0.475))

        self.inventory = Inventory(slots=len(self.settings_dict.get("weapons")))

        for n, weapon in enumerate(self.settings_dict.get("weapons")):
            self.inventory.append(self.settings_dict.get("weapons")[weapon]["image"], weapon, n)

        self.player = Player(self.settings_dict, self.high_score, self.info_label, self.inventory, pypresence_client)

        self.shootables_parent = Entity()
        mouse.traverse_target = self.shootables_parent

        self.enemies = []

        for i in range(15):
            self.summon_enemy()

        self.player.summon_enemy = self.summon_enemy

        self.sun = DirectionalLight()
        self.sun.look_at(Vec3(1,-1,-1))

        self.sky = Sky()
        self.sky.update = self.update
        
    def summon_enemy(self):
        if not len(self.enemies) >= 50:
            enemy_stats = random.choice(list(self.enemy_types.items()))[1]
            speed, size, image_path = enemy_stats["speed"], enemy_stats["size"], enemy_stats["image"]
            self.enemies.append(
                Enemy(
                    speed,
                    size,
                    self.player, 
                    self.shootables_parent,
                    self.player.x + (random.randint(12, 24) * random.choice([1, -1])),
                    random.randint(min_enemy_y, max_enemy_y),
                    self.player.z + (random.randint(12, 24) * random.choice([1, -1])),
                    Texture(Path(image_path))
                )
            )

    def update(self):
        Sky.update(self.sky)

        if held_keys["escape"]:
            self.back_to_main_menu()
        elif held_keys["n"]:
            self.summon_enemy()

    def back_to_main_menu(self):
        self.hide()
        from menus.main import Main
        Main(self.pypresence_client)

    def hide(self):
        destroy(self.ground)
        destroy(self.sun)
        destroy(self.sky)
        Sky.instances.remove(self.sky)
        destroy(self.info_label)
        self.inventory.hide()
        self.player.hide()
        destroy(self.shootables_parent)

        for enemy in self.enemies:
            destroy(enemy)

        with open("data.json", "w") as file:
            file.write(json.dumps({"high_score": self.player.high_score}, indent=4))
