from game.inventory import Inventory
from game.player import Player
from game.enemy import Enemy

from utils.constants import min_enemy_y, max_enemy_y, enemies, weapons

from ursina import *
from ursina.shaders import lit_with_shadows_shader

from pathlib import Path

import os, json

class Game():
    def __init__(self, pypresence_client, game_mode) -> None:
        self.pypresence_client = pypresence_client
        self.game_mode = game_mode
        self.game_over_triggered = False
        self.enemies = []

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.high_score = json.load(file)["high_score"]
        else:
            self.high_score = 0

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        pypresence_client.update(state='Training Aim', details=f'Hits: 0/0 Accuracy: 0%')

        self.enemy_types = self.settings_dict.get("enemies", enemies)

        self.ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4), shader=lit_with_shadows_shader)
        self.info_label = Text("Score: 0 Hits: 0/0 Accuracy: 0%", parent=camera.ui, position=(-0.1 if self.game_mode == "training" else -0.4, 0.475))
        self.inventory = Inventory(slots=len(self.settings_dict.get("weapons", weapons)))

        for n, weapon in enumerate(self.settings_dict.get("weapons", weapons)):
            self.inventory.append(self.settings_dict.get("weapons", weapons)[weapon]["image"], weapon, n)

        self.player = Player(self.game_mode, self.settings_dict, self.high_score, self.info_label, self.inventory, pypresence_client)
        self.player.summon_enemy = self.summon_enemy

        self.shootables_parent = Entity()
        mouse.traverse_target = self.shootables_parent
        
        if self.game_mode == "waves":
            enemy_num = self.player.wave_enemies_left
        else:
            enemy_num = 15    

        for _ in range(enemy_num):
            self.summon_enemy()

        self.sun = DirectionalLight()
        self.sun.look_at(Vec3(1,-1,-1))

        self.sky = Sky()
        self.sky.update = self.update
        self.sky.input = self.input

        if self.game_mode == "training":
            self.create_enemies_label = Text("Use n or Controller A to create new targets.", parent=camera.ui, position=(-0.875, -0.4), scale=1)

    def summon_enemy(self):
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

        if self.game_mode == "waves" and time.perf_counter() - self.player.last_wave_time >= self.player.wave_time:
            self.game_over()
        
        if self.game_mode == "1 minute test" and time.perf_counter() - self.player.test_start >= 60:
            self.game_over()

        if self.game_mode == r"100% accuracy test" and self.player.shots_fired - self.player.shots_hit >= 1:
            self.game_over()

    def input(self, key):
        if key == "escape" or key == "gamepad start":
            self.back_to_main_menu()
        elif not self.game_mode == "1 minute test" and (key == "n" or key == "gamepad a"):
            self.summon_enemy()

    def game_over(self):
        self.hide()

        self.game_over_triggered = True

        self.main = Entity(parent=camera.ui, model='cube', color=color.dark_gray, scale=(1.8, 1.2), z=1)
        
        info_text = f"Wave: {self.player.wave_number}\n" if self.game_mode == "waves" else ""
        info_text += f"Score: {self.player.score}\nHits: {self.player.shots_fired}/{self.player.shots_hit}\nAccuracy: {round(self.player.accuracy, 2)}%"

        self.game_over_label = Text(text=f"Game Over\n\n{info_text}", scale=3, position=(-0.2, 0.3))

        self.exit_button = Button(text="Exit", scale_x=0.4, scale_y=0.1, position=(0, -0.3), on_click=self.back_to_main_menu)

    def back_to_main_menu(self):
        self.hide()
        from menus.main import Main
        Main(self.pypresence_client)

    def hide(self):
        if self.game_over_triggered:
            destroy(self.main)
            destroy(self.game_over_label)
            destroy(self.exit_button)
            return

        destroy(self.ground)
        destroy(self.sun)
        destroy(self.sky)
        destroy(self.info_label)
        destroy(self.shootables_parent)

        if self.sky in Sky.instances:
            Sky.instances.remove(self.sky)

        self.inventory.hide()
        self.player.hide()

        if self.game_mode == "training":
            destroy(self.create_enemies_label)

        for enemy in self.enemies:
            destroy(enemy)

        with open("data.json", "w") as file:
            file.write(json.dumps({"high_score": self.player.high_score}, indent=4))
