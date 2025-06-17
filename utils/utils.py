from panda3d.core import GraphicsPipeSelection
from ursina.prefabs.dropdown_menu import DropdownMenu

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

class FakePyPresence():
    def __init__(self):
        ...
    def update(self, *args, **kwargs):
        ...
    def close(self, *args, **kwargs):
        ...
