from ursina import Audio, application

from utils.paths import BASE_DIR

# Point Ursina's asset lookup at the bundled assets instead of the exe directory.
application.asset_folder = BASE_DIR

music_sound = Audio("assets/sound/music.mp3", autoplay=False)
death_sound = Audio("assets/sound/death.wav", autoplay=False)
