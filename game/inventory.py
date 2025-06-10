from ursina import Entity, Quad, color, camera, held_keys, destroy

class Inventory():
    def __init__(self, x=0, y=4.5, width=12, height=1, slots=5):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.slot_number = slots
        self.slot_width = width / self.slot_number

        self.slot_grid = {}
        self.item_grid = {}
        self.slot_names = {}

        self.current_slot = 0

        self.create_grid()

        self.slot_grid[0].input = self.input

    def switch_to(self, slot):
        self.item_grid[self.current_slot].color = color.gray
        self.slot_grid[self.current_slot].color = color.gray

        self.current_slot = slot

        self.item_grid[slot].color = color.white
        self.slot_grid[slot].color = color.white

    def input(self, key):
        if key.isnumeric() and int(key) <= self.slot_number:
            self.switch_to(int(key) - 1)

        if key == "scroll up":
            self.switch_to(min(self.slot_number - 1, self.current_slot + 1))
        elif key == "scroll down":
            self.switch_to(max(0, self.current_slot - 1))

    def create_grid(self):
        for slot in range(self.slot_number):
            self.slot_grid[slot] = Entity(
                parent = camera.ui,
                model = Quad(radius=.015),
                texture = 'white_cube',
                scale = (self.slot_width * 0.1, self.height * 0.1),
                origin = (-slot * (self.slot_width / 2), 0),
                position = (-.55, -.4),
                color = color.gray if slot != self.current_slot else color.white
            )

    def append(self, item, name, slot):
        self.slot_names[slot] = name

        self.item_grid[slot] = Entity(
            parent = camera.ui,
            model = Quad(radius=.015),
            texture = item,
            scale = (self.slot_width * 0.1, self.height * 0.1),
            origin = (-slot * (self.slot_width / 2), 0),
            position = (-.55, -.4),
            z=-1,
            color = color.gray if slot != self.current_slot else color.white
        )

    def hide(self):
        for item_entity in self.item_grid.values():
            destroy(item_entity)

        for slot_entity in self.slot_grid.values():
            destroy(slot_entity)
