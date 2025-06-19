min_enemy_y = 0
max_enemy_y = 20
min_enemy_movement = 7
max_enemy_movement = 10
enemy_health = 100

weapons = {
    "assault_rifle": {"dmg": 20, "atk_speed": 0.2, "image": "assets/graphics/assaultrifle.png"},
    "smg": {"dmg": 10, "atk_speed": 0.1, "image": "assets/graphics/smg.png"},
    "minigun": {"dmg": 2, "atk_speed": 0.02, "image": "assets/graphics/minigun.png"},
    "pistol": {"dmg": 100 / 3, "atk_speed": 1 / 3, "image": "assets/graphics/pistol.png"},
    "revolver": {"dmg": 50, "atk_speed": 1 / 2, "image": "assets/graphics/revolver.png"},
    "sniper": {"dmg": 100, "atk_speed": 1, "image": "assets/graphics/sniper.png"},
}

enemies = {
    "default": {"speed": 0.12, "size": 1, "image": "assets/graphics/default_enemy.png"} 
}

discord_presence_id = 1380237183352311838

settings = {
    "Enemies": {"default": enemies},
    "Weapons": {"default": weapons},
    "Graphics": {
        "Window Mode": {"type": "option", "options": ["Windowed", "Fullscreen", "Borderless"], "config_key": "window_mode", "default": "Windowed"},
        "Resolution": {"type": "option", "options": ["1366x768", "1440x900", "1600x900", "1920x1080", "2560x1440", "3840x2160"], "config_key": "resolution"},
        "Anti-Aliasing": {"type": "option", "options": ["None", "2x MSAA", "4x MSAA", "8x MSAA", "16x MSAA"], "config_key": "anti_aliasing", "default": "4x MSAA"},
        "VSync": {"type": "bool", "config_key": "vsync", "default": True},
    },
    "Sound": {
        "Music": {"type": "bool", "config_key": "music", "default": True},
        "SFX": {"type": "bool", "config_key": "sfx", "default": True},
        "Music Volume": {"type": "slider", "min": 0, "max": 100, "config_key": "music_volume", "default": 50},
        "SFX Volume": {"type": "slider", "min": 0, "max": 100, "config_key": "sfx_volume", "default": 50},
    },
    "Miscellaneous": {
        "Discord RPC": {"type": "bool", "config_key": "discord_rpc", "default": True},
    },
    "Credits": None
}

settings_start_category = "Enemies"
