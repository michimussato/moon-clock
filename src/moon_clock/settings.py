import logging
import pathlib
import enum


class Settings(enum.Enum):
    BASE_DIR = pathlib.Path(__file__).resolve().parent
    RESOURCES = BASE_DIR / "data"

    GLOBAL_LOGGING_LEVEL = logging.DEBUG

    # INKY
    PIMORONI_SATURATION = 0.5  # Default: 0.5
    BUTTONS = [5, 6, 16, 24]

    # CLOCK
    ANTIALIAS = 4  # Warning: expensive calculation
    ARIAL = RESOURCES / "ttf" / "arial.ttf"
    CALLIGRAPHIC = RESOURCES / "ttf" / "calligraphia-one.ttf"
    CLOCK_UPDATE_INTERVAL = 15  # in minutes
    MOON_TEXTURE = RESOURCES / "img" / "moon_texture_small.png"
    HOURS = [12, 24]

    # MOON TEXTURE
    CONTRAST = 1
    BRIGHTNESS = 1.2

    # TEXT
    DATE_FORMAT = ['%-d.%-m.%Y'][0]
