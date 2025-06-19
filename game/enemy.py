from ursina import *
from utils.constants import enemy_health, min_enemy_movement, max_enemy_movement
from ursina.shaders import lit_with_shadows_shader

class Enemy(Entity):
    def __init__(self, speed, size, player, shootables_parent, x, y, z, texture):
        super().__init__(parent=shootables_parent, model='cube', collider='box', texture=texture, x=x, y=y, z=z, shader=lit_with_shadows_shader, scale=size)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = enemy_health
        self.hp = self.max_hp
        self.movement_type = random.choice(["left", "right", "top"])
        self.movement_done = 0
        self.speed = speed
        self.movement_amount = random.uniform(min_enemy_movement, max_enemy_movement)
        self.player = player

        self.path_line = Entity(parent=self.parent, model='cube', color=color.red, position=(0, 0), rotation=(0, 0, 0), shader=lit_with_shadows_shader)

        self.update_path_line()

    def update_path_line(self):
        remaining = self.movement_amount - self.movement_done
        if remaining <= 0:
            return

        start = self.position
        end = self.position

        if self.movement_type == "left":
            end -= Vec3(max(0.05, remaining), 0, 0)
            scale = Vec3(max(0.05, remaining), 0.05, 0.05)
        elif self.movement_type == "right":
            end += Vec3(max(0.05, remaining), 0, 0)
            scale = Vec3(max(0.05, remaining), 0.05, 0.05)
        elif self.movement_type == "top":
            end += Vec3(0, max(0.05, remaining), 0)
            scale = Vec3(0.05, max(0.05, remaining), 0.05)
        elif self.movement_type == "bottom":
            end -= Vec3(0, max(0.05, remaining), 0)
            scale = Vec3(0.05, max(0.05, remaining), 0.05)

        mid = (start + end) / 2

        self.path_line.position = mid
        self.path_line.scale = scale

    def update(self):
        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.health_bar.look_at_2d(self.player, axis="x")
        self.look_at_2d(self.player, axis="y")

        if self.movement_type == "left":
            if self.movement_done < self.movement_amount:
                self.x -= self.speed
                self.movement_done += self.speed
            else:
                self.movement_type = "right"
                self.movement_done = 0
        elif self.movement_type == "right":
            if self.movement_done < self.movement_amount:
                self.x += self.speed
                self.movement_done += self.speed
            else:
                self.movement_type = "left"
                self.movement_done = 0
        elif self.movement_type == "top":
            if self.movement_done < self.movement_amount:
                self.y += self.speed
                self.movement_done += self.speed
            else:
                self.movement_type = "bottom"
                self.movement_done = 0
        elif self.movement_type == "bottom":
            if self.movement_done < self.movement_amount:
                self.y -= self.speed
                self.movement_done += self.speed
            else:
                self.movement_type = "top"
                self.movement_done = 0

        self.update_path_line()

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1
