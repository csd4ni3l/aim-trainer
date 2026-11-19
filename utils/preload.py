from ursina import Audio

from utils.paths import resolve_asset

music_sound = Audio(resolve_asset("assets/sound/music.mp3"), autoplay=False)
death_sound = Audio(resolve_asset("assets/sound/death.wav"), autoplay=False)
