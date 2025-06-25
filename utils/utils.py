from panda3d.core import GraphicsPipeSelection
from ursina.prefabs.dropdown_menu import DropdownMenu
from ursina.prefabs.file_browser import FileBrowser
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina import *

def get_closest_resolution():
    allowed_resolutions = [(1366, 768), (1440, 900), (1600,900), (1920,1080), (2560,1440), (3840,2160)]
    pipe = GraphicsPipeSelection.getGlobalPtr().makeDefaultPipe()

    if not pipe:
        screen_width, screen_height = min(allowed_resolutions, key=lambda res: res[0] * res[1])
    else:
        screen_width = pipe.getDisplayWidth()
        screen_height = pipe.getDisplayHeight()

    if (screen_width, screen_height) in allowed_resolutions:
        if not allowed_resolutions.index((screen_width, screen_height)) == 0:
            closest_resolution = allowed_resolutions[allowed_resolutions.index((screen_width, screen_height))-1]
        else:
            closest_resolution = (screen_width, screen_height)
    else:
        target_width, target_height = screen_width // 2, screen_height // 2

        closest_resolution = min(
            allowed_resolutions,
            key=lambda res: abs(res[0] - target_width) + abs(res[1] - target_height)
        )
    return closest_resolution

class Dropdown(DropdownMenu):
    def __init__(self, text='', buttons = None, **kwargs):
        super().__init__(text, buttons, **kwargs)

        self.scale = (.4,.04)


    def on_mouse_enter(self):
        ...
    
    def input(self, key):
        super().input(key)

        if key == 'left mouse down' and self.hovered:
            if not self.buttons[0].enabled:
                self.open()
            else:
                self.close()

class FileManager(FileBrowser):
    def open(self, path=None):
        if not self.selection:
            return

        if not self.return_folders:
            if self.selection[0].is_dir():
                self.path = self.selection[0]
                return
            
        elif not self.selection[0].is_dir():
            return

        if hasattr(self, 'on_submit'):
            self.on_submit(self.selection)

        self.close()

class FakePyPresence():
    def __init__(self):
        ...
    def update(self, *args, **kwargs):
        ...
    def close(self, *args, **kwargs):
        ...

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
class FixedFirstPersonController(FirstPersonController):
    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        look_x = mouse.velocity[0] + held_keys.get('gamepad right stick x', 0) * 0.01
        look_y = mouse.velocity[1] + held_keys.get('gamepad right stick y', 0) * 0.01

        self.rotation_y += look_x * self.mouse_sensitivity[1]
        self.camera_pivot.rotation_x -= look_y * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * ((held_keys['w'] - held_keys['s']) + held_keys["gamepad left stick y"])
            + self.right * ((held_keys['d'] - held_keys['a']) + held_keys["gamepad left stick x"])
            ).normalized()

        feet_ray = raycast(self.position+Vec3(0,0.5,0), self.direction, traverse_target=self.traverse_target, ignore=self.ignore_list, distance=.5, debug=False)
        head_ray = raycast(self.position+Vec3(0,self.height-.1,0), self.direction, traverse_target=self.traverse_target, ignore=self.ignore_list, distance=.5, debug=False)
        if not feet_ray.hit and not head_ray.hit:
            move_amount = self.direction * time.dt * self.speed

            if raycast(self.position+Vec3(-.0,1,0), Vec3(1,0,0), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[0] = min(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(-1,0,0), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[0] = max(move_amount[0], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,1), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[2] = min(move_amount[2], 0)
            if raycast(self.position+Vec3(-.0,1,0), Vec3(0,0,-1), distance=.5, traverse_target=self.traverse_target, ignore=self.ignore_list).hit:
                move_amount[2] = max(move_amount[2], 0)
            self.position += move_amount

            # self.position += self.direction * self.speed * time.dt


        if self.gravity:
            # gravity
            ray = raycast(self.world_position+(0,self.height,0), self.down, traverse_target=self.traverse_target, ignore=self.ignore_list)

            if ray.distance <= self.height+.1:
                if not self.grounded:
                    self.land()
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
                return
            else:
                self.grounded = False

            # if not on ground and not on way up in jump, fall
            self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
            self.air_time += time.dt * .25 * self.gravity