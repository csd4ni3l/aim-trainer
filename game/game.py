from game.inventory import Inventory
from game.player import Player
from game.enemy import Enemy
from utils.constants import weapons, min_enemy_y, max_enemy_y
from ursina import *
from ursina.shaders import lit_with_shadows_shader
import os

enemy_file_names = os.listdir("assets/graphics/enemy")

class Game():
    def __init__(self, pypresence_client) -> None:
        self.pypresence_client = pypresence_client

        pypresence_client.update(state='Training Aim', details=f'Hits: 0/0 Accuracy: 0%')

        self.ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4), shader=lit_with_shadows_shader)

        self.info_label = Text("Score: 0 Hits: 0/0 Accuracy: 0%", parent=camera.ui, position=(-0.1, 0.475))

        self.inventory = Inventory(slots=len(weapons))

        for n, weapon in enumerate(weapons):
            self.inventory.append(weapons[weapon]["image"], weapon, n)

        self.player = Player(self.info_label, self.inventory, pypresence_client)

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
            self.enemies.append(Enemy(self.player, self.shootables_parent, self.player.x + (random.randint(12, 24) * random.choice([1, -1])), random.randint(min_enemy_y, max_enemy_y), self.player.z + (random.randint(12, 24) * random.choice([1, -1])), "assets/graphics/enemy/" + random.choice(file_names)))

    def update(self):
        Sky.update(self.sky)

        if held_keys["escape"]:
            self.back_to_main_menu()
        elif held_keys["space"]:
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
