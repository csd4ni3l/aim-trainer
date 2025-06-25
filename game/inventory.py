from ursina import Entity, Quad, color, camera, destroy, Texture
from pathlib import Path

class Inventory():
    def __init__(self, x=0, y=4.5, slot_width=0.1, slot_height=0.1, slots=5):
        self.x = x
        self.y = y
        self.slot_number = slots
        self.slot_width = slot_width
        self.slot_height = slot_height

        self.slot_grid = {}
        self.slot_names = {}

        self.current_slot = 0

    def switch_to(self, slot):
        self.slot_grid[self.current_slot].color = color.gray

        self.current_slot = slot

        self.slot_grid[slot].color = color.white

    def input(self, key):
        if key.isnumeric() and int(key) <= self.slot_number:
            self.switch_to(int(key) - 1)

        if key == "scroll down" or key == "gamepad dpad right":
            self.switch_to(min(self.slot_number - 1, self.current_slot + 1))
        elif key == "scroll up" or key == "gamepad dpad left":
            self.switch_to(max(0, self.current_slot - 1))

    def append(self, item, name, slot):
        self.slot_names[slot] = name

        self.slot_grid[slot] = Entity(
            parent = camera.ui,
            model = Quad(radius=.015),
            texture = Texture(Path(item)),
            scale = (self.slot_width, self.slot_height),
            position = (-.3 + slot * (self.slot_width * 1.25), -.4),
            z=-1,
            color = color.gray if slot != self.current_slot else color.white
        )

        if slot == 0:
            self.slot_grid[slot].input = self.input

    def hide(self):
        for slot_entity in self.slot_grid.values():
            destroy(slot_entity)
