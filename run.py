import os, json
from ursina import Ursina
from menus.main import Main
from utils.utils import get_closest_resolution
from ursina import window

if os.path.exists('settings.json'):
    with open('settings.json', 'r') as settings_file:
        settings = json.load(settings_file)

else:
    resolution = get_closest_resolution()

    settings = {
        "music": True,
        "music_volume": 50,
        "resolution": f"{resolution[0]}x{resolution[1]}",
        "window_mode": "Windowed",
        "vsync": True,
        "discord_rpc": True
    }

    with open("settings.json", "w") as file:
        file.write(json.dumps(settings))

args = {
    "fullscreen": settings['window_mode'] == 'Fullscreen',
    "borderless": settings['window_mode'] == 'Borderless',
    "vsync": settings["vsync"]
}

if not args["fullscreen"]:
    args["size"] = list(map(int, settings['resolution'].split('x')))

app = Ursina(title="Aim Trainer", development_mode=False, **args)

window.cog_button.enabled = False
window.editor_ui.enabled = True
window.fps_counter.enabled = True
window.collider_counter.enabled = False
window.entity_counter.enabled = False

if settings.get("music", True):
    from utils.preload import music_sound
    music_sound.play()
    music_sound.volume = settings.get("music_volume", 50) / 100
    music_sound.loop = True

Main()

app.run()
