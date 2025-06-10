from ursina.prefabs.ursfx import ursfx
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *
from utils.constants import weapons, max_enemy_speed
from ursina.shaders import lit_with_shadows_shader
from utils.preload import death_sound
import json

class Player(FirstPersonController):
    def __init__(self, info_label, inventory, pypresence_client) -> None:
        super().__init__(model='cube', z=16, color=color.orange, origin_y=-.5, speed=8, collider='box', gravity=False, shader=lit_with_shadows_shader)

        self.collider = BoxCollider(self, Vec3(0,1,0), Vec3(1,2,1))

        self.gun = Entity(model='cube', parent=camera, position=(.5,-.25,.25), scale=(.3,.2,1), origin_z=-.5, color=color.red, on_cooldown=True, shader=lit_with_shadows_shader)
        invoke(setattr, self.gun, 'on_cooldown', False, delay=1)
        self.gun.muzzle_flash = Entity(parent=self.gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False, shader=lit_with_shadows_shader)

        self.info_label = info_label
        self.inventory = inventory
        self.pypresence_client = pypresence_client

        self.last_presence_update = time.perf_counter()
        self.shots_fired = 0
        self.shots_hit = 0
        self.accuracy = 0
        self.score = 0

        self.weapon_attack_speed = 0
        self.weapon_dmg = 0

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

    def update(self):
        super().update()

        if held_keys['left mouse']:
            self.shoot()

        self.x = max(-16, min(self.x, 16))
        self.z = max(-16, min(self.z, 16))
        self.info_label.text = f"Score: {self.score} Hits: {self.shots_fired}/{self.shots_hit} Accuracy: {round(self.accuracy, 2)}%"

        weapon_name = self.inventory.slot_names[self.inventory.current_slot]
        self.weapon_attack_speed = weapons[weapon_name]["atk_speed"]
        self.weapon_dmg = weapons[weapon_name]["dmg"]

        if time.perf_counter() - self.last_presence_update >= 3:
            self.last_presence_update = time.perf_counter()
            self.pypresence_client.update(state='Training Aim', details=f"Score: {self.score} Hits: {self.shots_fired}/{self.shots_hit} Accuracy: {round(self.accuracy, 2)}%")

    def summon_enemy(self):
        pass

    def shoot(self):
        if not self.gun.on_cooldown:
            self.gun.on_cooldown = True
            self.gun.muzzle_flash.enabled = True

            if self.settings_dict.get("sfx", True):
                ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)

            invoke(self.gun.muzzle_flash.disable, delay=.05)
            invoke(setattr, self.gun, 'on_cooldown', False, delay=self.weapon_attack_speed)
            self.shots_fired += 1

            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= self.weapon_dmg
                mouse.hovered_entity.blink(color.red)

                self.score += int(distance(mouse.hovered_entity, self) * (mouse.hovered_entity.speed / max_enemy_speed))

                self.shots_hit += 1

                if mouse.hovered_entity.hp <= 0:
                    destroy(mouse.hovered_entity.health_bar)
                    destroy(mouse.hovered_entity.path_line)
                    destroy(mouse.hovered_entity)

                    death_sound.play()

                    self.summon_enemy()

            self.accuracy = (self.shots_hit / self.shots_fired) * 100

    def hide(self):
        destroy(self.gun)
        destroy(self.gun.muzzle_flash)
        destroy(self)
