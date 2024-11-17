import logging
from pathlib import Path
import os


# BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent


    GLOBAL_LOGGING_LEVEL = logging.DEBUG

    # inky
    PIMORONI_SATURATION = 0.5  # Default: 0.5
    BUTTONS = [5, 6, 16, 24]

    # clock
    # LAT, LONG = 47.39134, 8.85971
    LAT, LONG = -33.8930459, 151.20688
    ANTIALIAS = 4  # Warning: expensive calculation
    ARIAL = r'/home/michael/git/repos/moon-clock/moon-clock/src/moon_clock/arial_narrow.ttf'
    CALLIGRAPHIC = r'/home/michael/git/repos/moon-clock/moon-clock/src/moon_clock/calligraphia-one.ttf'
    CLOCK_UPDATE_INTERVAL = 15  # in minutes
