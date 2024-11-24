import logging
import pathlib
from pathlib import Path
import enum


class Settings(enum.Enum):
    BASE_DIR = Path(__file__).resolve().parent
    RESOURCES = pathlib.Path(BASE_DIR / "data")

    GLOBAL_LOGGING_LEVEL = logging.DEBUG

    # INKY
    PIMORONI_SATURATION = 0.5  # Default: 0.5
    BUTTONS = [5, 6, 16, 24]

    # CLOCK
    ANTIALIAS = 4  # Warning: expensive calculation
    ARIAL = pathlib.Path(RESOURCES / "ttf" / "arial.ttf")
    CALLIGRAPHIC = pathlib.Path(RESOURCES / "ttf" / "calligraphia-one.ttf")
    CLOCK_UPDATE_INTERVAL = 15  # in minutes
    MOON_TEXTURE = pathlib.Path(RESOURCES / "img" / "moon_texture_small.png")

    HOURS_ = [12, 24]
    HOURS = HOURS_[1]

    # MOON TEXTURE
    CONTRAST = 1
    BRIGHTNESS = 1.2

    # TEXT
    DEFAULT_TEXT = 'MoonClock'
    DATE_FORMAT = ['%-d.%-m.%Y'][0]
    DEFAULT_RESOLUTION = 448
