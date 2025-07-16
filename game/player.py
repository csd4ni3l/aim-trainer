from ursina import *

from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.ursfx import ursfx

from utils.preload import death_sound
from utils.constants import weapons
from utils.utils import FixedFirstPersonController

import json
from pathlib import Path

class Player(FixedFirstPersonController):
    def __init__(self, game_mode, settings_dict, high_score, info_label, inventory, pypresence_client) -> None:
        super().__init__(model='cube', z=16, color=color.orange, origin_y=-.5, speed=8, collider='box', gravity=True, shader=lit_with_shadows_shader)

        self.collider = BoxCollider(self, Vec3(0,1,0), Vec3(1,2,1))

        self.info_label = info_label
        self.inventory = inventory
        self.pypresence_client = pypresence_client
        self.high_score = high_score
        self.settings_dict = settings_dict
        self.game_mode = game_mode
        
        if self.game_mode == "waves":
            self.wave_number = 1
            self.wave_enemies_left = 20
            self.wave_time = 90
            self.last_wave_time = time.perf_counter()
        elif self.game_mode == "1 minute test":
            self.test_start = time.perf_counter()

        self.last_presence_update = time.perf_counter()
        self.shots_fired = 0
        self.shots_hit = 0
        self.accuracy = 0
        self.score = 0
        self.weapon_attack_speed = 0
        self.weapon_dmg = 0

        self.gun = Entity(model='cube', texture=Texture(Path(self.settings_dict.get("weapons", weapons)[self.inventory.slot_names[self.inventory.current_slot]]["image"])), parent=camera, position=(.5,-.25,.25), scale=(.3,.2,1), origin_z=-.5, on_cooldown=True, shader=lit_with_shadows_shader)
        invoke(setattr, self.gun, 'on_cooldown', False, delay=1)
        self.gun.muzzle_flash = Entity(parent=self.gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False, shader=lit_with_shadows_shader)

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

    def update(self):
        if self.enabled:
            super().update()

            if held_keys['left mouse'] or held_keys["gamepad right trigger"]:
                self.shoot()

            self.x = max(-16, min(self.x, 16))
            self.z = max(-16, min(self.z, 16))

            if self.game_mode == "waves":
                info_text = f"Wave: {self.wave_number} Enemies Left: {self.wave_enemies_left} Time Left: {round(self.wave_time - (time.perf_counter() - self.last_wave_time), 2)}s "
            elif self.game_mode == "1 minute test":
                info_text = f"Time Left: {round(60 - (time.perf_counter() - self.test_start))} "
            else:
                info_text = ""

            info_text += f"Score: {self.score} High Score: {self.high_score} Hits: {self.shots_fired}/{self.shots_hit} Accuracy: {round(self.accuracy, 2)}%"
            self.info_label.text = info_text

            weapon_name = self.inventory.slot_names[self.inventory.current_slot]
            self.gun.texture = Texture(Path(self.settings_dict.get("weapons", weapons)[weapon_name]["image"]))
            self.weapon_attack_speed = self.settings_dict.get("weapons", weapons)[weapon_name]["atk_speed"]
            self.weapon_dmg = self.settings_dict.get("weapons", weapons)[weapon_name]["dmg"]
            if self.score > self.high_score:
                self.high_score = self.score

            if time.perf_counter() - self.last_presence_update >= 3:
                self.last_presence_update = time.perf_counter()
                self.pypresence_client.update(state='Training Aim', details=f"Score: {self.score} High Score: {self.high_score} Hits: {self.shots_fired}/{self.shots_hit} Accuracy: {round(self.accuracy, 2)}%")
            
    def summon_enemy(self):
        pass

    def try_to_disable_muzzle_flash(self): # without this method, 100% accuracy test crashes, because using .disable on a destroyed entity is not allowed
        try:
            self.gun.muzzle_flash.disable()
        except:
            pass

    def shoot(self):
        if not self.gun.on_cooldown:
            self.gun.on_cooldown = True

            self.gun.muzzle_flash.enabled = True

            if self.settings_dict.get("sfx", True):
                ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)

            invoke(self.try_to_disable_muzzle_flash, delay=.05)
            invoke(setattr, self.gun, 'on_cooldown', False, delay=self.weapon_attack_speed)
            self.shots_fired += 1

            if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
                mouse.hovered_entity.hp -= self.weapon_dmg
                mouse.hovered_entity.blink(color.red)

                base_distance_score = distance(mouse.hovered_entity, self) * 10
                damage_multiplier = self.weapon_dmg / mouse.hovered_entity.max_hp
                attack_speed_multiplier = ((1 / self.weapon_attack_speed) ** 0.5) / 10
                self.score += int(base_distance_score * damage_multiplier * attack_speed_multiplier)

                self.shots_hit += 1

                if mouse.hovered_entity.hp <= 0:
                    destroy(mouse.hovered_entity.health_bar)
                    destroy(mouse.hovered_entity.path_line)
                    destroy(mouse.hovered_entity)

                    death_sound.play()

                    if self.game_mode == "waves":
                        self.wave_enemies_left -= 1

                        if self.wave_enemies_left <= 0:
                            self.wave_time += 20
                            self.wave_number += 1 
                            self.wave_enemies_left = 20 + (self.wave_number * 5)
                            self.last_wave_time = time.perf_counter()

                            for _ in range(self.wave_enemies_left):
                                self.summon_enemy()
                    
                    else:
                        self.summon_enemy()

            self.accuracy = (self.shots_hit / self.shots_fired) * 100

    def hide(self):
        destroy(self.gun)
        destroy(self.gun.muzzle_flash)
        destroy(self)
