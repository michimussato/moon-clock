import pathlib
import sys
import argparse
import datetime
import zoneinfo
import logging
import math
import numpy as np
import time

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from timezonefinder import TimezoneFinder

from PIL import ImageFile, Image, ImageDraw, ImageFont, ImageOps, ImageChops, ImageEnhance, ImageFilter
from suncalcPy import suncalc

import moon_clock
from moon_clock.images import Resource
from moon_clock.settings import Settings

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "MIT"

LOG = logging.getLogger(__name__)


LOG = logging.getLogger(__name__)
# LOG.setLevel(Settings.GLOBAL_LOGGING_LEVEL.value)


ImageFile.LOAD_TRUNCATED_IMAGES = True


# ---- Python API ----


class MoonClockException(Exception):
    pass


class MoonClock(object):

    @staticmethod
    def _get_coords(address) -> tuple[float, float]:
        geolocator = Nominatim(user_agent="moon-clock")
        max_tries = 5
        tries = 0
        while True:
            try:
                location = geolocator.geocode(address)
                break
            except GeocoderTimedOut as e:
                tries += 1
                time.sleep(1)
                if tries >= max_tries:
                    raise MoonClockException(f"Giving up - tried {max_tries} times.") from e

        LOG.info(f"Writing Clock PNG for location: {location.address}")
        return location.latitude, location.longitude


    @staticmethod
    def get_clock(
            address: str,
            iso: None,
            draw_text: str = Settings.DEFAULT_TEXT.value,
            draw_tz: bool = Settings.DRAW_TZ.value,
            draw_date: bool = Settings.DRAW_DATE.value,
            size: int = Settings.DEFAULT_RESOLUTION.value,
            hours: int = Settings.HOURS.value,
            draw_sun: bool = True,
            draw_moon: bool = True,
            draw_moon_tex: bool = True,
            draw_moon_phase: bool = True,
            blur: bool = False,
            mask_moon_shadow: bool = True,
            mask_square: bool = False,
    ) -> Image:

        LAT, LONG = MoonClock._get_coords(address=address)

        tz = TimezoneFinder().timezone_at(lng=LONG, lat=LAT)
        LOG.info(f"Timezone: {tz}")

        if iso is None:
            now = datetime.datetime.now(tz=zoneinfo.ZoneInfo(key=tz))
        else:
            now = datetime.datetime.fromisoformat(iso)

        print(now)

        _size = size * Settings.ANTIALIAS.value

        if hours not in Settings.HOURS_.value:
            raise MoonClockException('hours can only be 12 or 24')

        bg = Image.new(mode='RGBA', size=(_size, _size), color=(0, 0, 0, 0))
        draw_bg = ImageDraw.Draw(bg)
        edge_compensation = 1  # top and left edge to make sure, AA takes place in pixels adjacent to edges
        _edge_comp_2 = 1  # bottom and right edge in addition to edge_compensation

        # MASKS
        # Get rid of ugly rim
        # and create perfect circle out of
        # imperfect moon texture
        # rect:
        if mask_square:
            draw_bg.rectangle(
                (
                    edge_compensation,
                    edge_compensation,
                    _size-edge_compensation - _edge_comp_2,
                    _size-edge_compensation - _edge_comp_2
                ),
                fill=(0, 0, 0, 255)
            )
        # circle:
        if mask_moon_shadow:
            draw_bg.ellipse(
                (
                    edge_compensation,
                    edge_compensation,
                    _size-edge_compensation - _edge_comp_2,
                    _size-edge_compensation - _edge_comp_2
                ),
                fill=(0, 0, 0, 255)
            )

        _clock = Image.new(mode='RGBA', size=(_size, _size), color=(0, 0, 0, 0))

        draw = ImageDraw.Draw(_clock)

        if hours == 24:
            arc_twelve = 90.0
        else:
            arc_twelve = 270.0

        white = (255, 255, 255, 255)

        # center dot
        draw.ellipse(
            [
                (
                    round(_size * 0.482),
                    round(_size * 0.482)
                ),
                (
                    round(_size - _size * 0.482),
                    round(_size - _size * 0.482)
                )
            ],
            fill=white,
            outline=None,
            width=round(_size * 0.312)
        )

        color = white
        if hours == 24:
            intervals = [
                (0.5, 3.0),
                # (0.0, 3.0),
                (14.0, 16.0),
                (29.0, 31.0),
                # (42.0, 48.0),
                (42.0, 44.5),
                (45.5, 48.0),
                (59.0, 61.0),
                (74.0, 76.0),
                # (87.0, 93.0),
                (87.0, 89.5),
                (90.5, 93.0),
                (104.0, 106.0),
                (119.0, 121.0),
                # (132.0, 138.0),
                (132.0, 134.5),
                (135.5, 138.0),
                (149.0, 151.0),
                (164.0, 166.0),
                # (177.0, 183.0),
                (177.0, 179.5),
                (180.5, 183.0),
                (194.0, 196.0),
                (209.0, 211.0),
                # (222.0, 228.0),
                (222.0, 224.5),
                (225.5, 228.0),
                (239.0, 241.0),
                (254.0, 256.0),
                # (267.0, 273.0),
                (267.0, 269.5),
                (270.5, 273.0),
                (284.0, 286.0),
                (299.0, 301.0),
                # (312.0, 318.0),
                (312.0, 314.5),
                (315.5, 318.0),
                (329.0, 331.0),
                (344.0, 346.0),
                # (357.0, 359.99),
                (357.0, 359.5),
            ]
        else:
            intervals = [(0.0, 3.0),
                         (29.0, 31.0),
                         (59.0, 61.0),
                         (87.0, 93.0),
                         (119.0, 121.0),
                         (149.0, 151.0),
                         (177.0, 183.0),
                         (209.0, 211.0),
                         (239.0, 241.0),
                         (267.0, 273.0),
                         (299.0, 301.0),
                         (329.0, 331.0),
                         (357.0, 359.99),
                         ]

        for start, end in intervals[::-1]:  # reversed
            draw.arc(
                [
                    (
                        round(_size * 0.022),
                        round(_size * 0.022)
                    ),
                    (
                        round(_size - _size * 0.022),
                        round(_size - _size * 0.022)
                    )
                ],
                start=start,
                end=end,
                fill=color,
                width=round(_size * 0.060)
            )

        decimal_h = float(now.strftime('%H')) + float(now.strftime('%M')) / 60
        arc_length_h = decimal_h / hours * 360.0

        # indicator
        color = white
        size_h = [
            (
                round(_size * 0.112),
                round(_size * 0.112)
            ),
            (
                round(_size - _size * 0.112),
                round(_size - _size * 0.112)
            )
        ]
        width = round(_size * 0.134)
        indicator_thickness = 6
        draw.arc(
            size_h,
            start=(arc_twelve + arc_length_h - indicator_thickness/2),
            end=(arc_twelve + arc_length_h + indicator_thickness/2),
            fill=color,
            width=width
        )

        if draw_text:
            logo_img = Image.new(mode='RGBA', size=(_size, _size), color=(0, 0, 0, 0))
            logo_draw = ImageDraw.Draw(logo_img)
            font_logo = ImageFont.truetype(Settings.CALLIGRAPHIC.value, round(_size * 0.140))
            length_logo = font_logo.getlength(draw_text)
            logo_draw.text(
                (
                    round(_size / 2) - length_logo / 2,
                    round(_size * 0.536)
                ),
                draw_text,
                fill=white,
                font=font_logo
            )

            _logo_inv = ImageOps.invert(_clock.convert('RGB'))
            _clock.paste(_logo_inv, mask=logo_img)

        if draw_tz:
            tz_img = Image.new(mode='RGBA', size=(_size, _size), color=(0, 0, 0, 0))
            tz_draw = ImageDraw.Draw(tz_img)
            font_tz = ImageFont.truetype(Settings.CALLIGRAPHIC.value, round(_size * 0.050))
            text_tz = now.strftime(tz)
            length_tz = font_tz.getlength(text_tz)
            tz_draw.text(
                (
                    round(_size / 2) - length_tz / 2,
                    round(_size * 0.3)
                ),
                text_tz,
                fill=white,
                font=font_tz
            )

            _date_inv = ImageOps.invert(_clock.convert('RGB'))
            _clock.paste(_date_inv, mask=tz_img)

        if draw_date:
            date_img = Image.new(mode='RGBA', size=(_size, _size), color=(0, 0, 0, 0))
            tz_draw = ImageDraw.Draw(date_img)
            font_tz = ImageFont.truetype(Settings.CALLIGRAPHIC.value, round(_size * 0.120))
            text_tz = now.strftime(Settings.DATE_FORMAT.value)
            length_tz = font_tz.getlength(text_tz)
            tz_draw.text(
                (
                    round(_size / 2) - length_tz / 2,
                    round(_size * 0.315)
                ),
                text_tz,
                fill=white,
                font=font_tz
            )

            _date_inv = ImageOps.invert(_clock.convert('RGB'))
            _clock.paste(_date_inv, mask=date_img)

        comp = Image.new(mode='RGBA', size=(_size, _size), color=(0, 0, 0, 0))
        comp = Image.alpha_composite(comp, bg)
        comp = Image.alpha_composite(comp, _clock)

        if draw_moon_phase:
            _draw_moon_image = Image.new(mode='RGBA', size=(_size, _size), color=(0, 0, 0, 0))
            _draw_moon = ImageDraw.Draw(_draw_moon_image)
            _draw_moon.ellipse(((edge_compensation-1, edge_compensation), (_size-edge_compensation-_edge_comp_2, _size-edge_compensation-_edge_comp_2+1)), fill=white)
            phase = round(
                float(
                    suncalc.getMoonIllumination(
                        now
                    )['phase']) * 2,
                4
            )
            LOG.info(f'Moon phase: {phase} / 4')

            spherical = math.cos(phase * math.pi)

            center = _size / 2

            if 0.0 <= phase <= 0.5:  # new to half moon
                _draw_moon.rectangle(
                    (0, 0, _size / 2, _size),
                    fill=(0, 0, 0, 0)
                )
                _draw_moon.ellipse(
                    (
                        center - (spherical * center) + edge_compensation,
                        0 + edge_compensation,
                        center + (spherical * center) - edge_compensation,
                        _size - edge_compensation
                    ),
                    fill=(0, 0, 0, 0)
                )

            elif 0.5 <= phase <= 1.0:  # half to full moon
                _draw_moon.rectangle(
                    (0, 0, _size / 2, _size),
                    fill=(0, 0, 0, 0)
                )
                _draw_moon.ellipse(
                    (
                        center + (spherical * center) + edge_compensation,
                        0 + edge_compensation,
                        center - (spherical * center) - edge_compensation -_edge_comp_2,
                        _size - edge_compensation - _edge_comp_2
                    ),
                    fill=white
                )

                # TODO:
                # Blur is not precise yet
                if blur:
                    blur_weight = 5
                    for i in range(75):
                        kernel = np.array(
                            [
                                [0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0],
                                [blur_weight, blur_weight, blur_weight, blur_weight, blur_weight],
                                [0, 0, 0, 0, 0],
                                [0, 0, 0, 0, 0]
                            ]
                        )
                        _draw_moon_image = _draw_moon_image.filter(
                            ImageFilter.Kernel(
                                size=(5, 5),
                                kernel=kernel.flatten()
                            )
                        )
                        # _temp = _temp.crop((_size/4, 0, _size/4*3, _size))
                        # _temp = _temp.resize((_size, _size))
                        # _draw_moon_image = _draw_mo.paste(_temp)
                        # _draw_moon.rectangle((0, 0, _size / 2, _size), fill=(0, 0, 0, 0))
                        # _draw_moon.rectangle((_size / 2, 0, _size, _size), fill=(0, 0, 0, 0))

            elif 1.0 < phase <= 1.5:  # full to half moon
                _draw_moon.rectangle(
                    (_size / 2, 0, _size, _size),
                    fill=(0, 0, 0, 0)
                )
                _draw_moon.ellipse(
                    (
                        center + (spherical * center) + edge_compensation,
                        0 + edge_compensation,
                        center - (spherical * center) - edge_compensation-_edge_comp_2,
                        _size - edge_compensation-_edge_comp_2
                    ),
                    fill=white
                )

            elif 1.5 < phase <= 2.0:  # half to new moon
                _draw_moon.rectangle(
                    (_size / 2, 0, _size, _size),
                    fill=(0, 0, 0, 0)
                )
                _draw_moon.ellipse(
                    (
                        center - (spherical * center) + edge_compensation,
                        0 + edge_compensation,
                        center + (spherical * center) - edge_compensation,
                        _size - edge_compensation
                    ),
                    fill=(0, 0, 0, 0)
                )

            _comp_inv = ImageOps.invert(comp.convert('RGB'))

            if draw_moon_tex:
                moon_tex = Resource().MOON_TEXTURE_SQUARE.resize((_size, _size))

                filter_contrast = ImageEnhance.Contrast(moon_tex)
                moon_tex = filter_contrast.enhance(Settings.CONTRAST.value)

                filter_bright = ImageEnhance.Brightness(moon_tex)
                moon_tex = filter_bright.enhance(Settings.BRIGHTNESS.value)

                moon_tex.paste(moon_tex, mask=_draw_moon_image)
                moon_tex = ImageChops.multiply(moon_tex, _comp_inv.convert('RGBA'))

                comp.paste(moon_tex, mask=_draw_moon_image)

            else:
                comp.paste(_comp_inv, mask=_draw_moon_image)

        if draw_sun:
            _draw_sun = ImageDraw.Draw(comp)
            _sun = suncalc.getTimes(now, LAT, LONG)

            decimal_sunrise = float(_sun['sunrise'].strftime('%H')) + float(_sun['sunrise'].strftime('%M')) / 60
            arc_length_sunrise = decimal_sunrise / hours * 360.0
            LOG.info(f'Sunrise: {str(_sun["sunrise"].strftime("%H:%M"))}')

            decimal_sunset = float(_sun['sunset'].strftime('%H')) + float(_sun['sunset'].strftime('%M')) / 60
            arc_length_sunset = decimal_sunset / hours * 360.0
            LOG.info(f'Sunset: {str(_sun["sunset"].strftime("%H:%M"))}')

            color = (255, 128, 0, 255)
            _size_astral = 0.17  # TODO: bigger means smaller circle
            _width = 0.012
            size_astral = [
                (
                    round(_size * _size_astral),
                    round(_size * _size_astral)
                ),
                (
                    round(_size - _size * _size_astral),
                    round(_size - _size * _size_astral)
                )
            ]
            width_astral = round(_size * _width)
            _draw_sun.arc(
                size_astral,
                start=arc_length_sunrise+arc_twelve,
                end=arc_length_sunset+arc_twelve,
                fill=color,
                width=width_astral
            )

        # moon
        if draw_moon:
            _draw_moon = ImageDraw.Draw(comp)
            now = datetime.datetime.today()

            _moon_yesterday = suncalc.getMoonTimes(
                now - datetime.timedelta(hours=24),
                LAT,
                LONG
            )
            _moon_today = suncalc.getMoonTimes(
                now,
                LAT,
                LONG
            )
            _moon_tomorrow = suncalc.getMoonTimes(
                now + datetime.timedelta(hours=24),
                LAT,
                LONG
            )

            LOG.debug(f'Moon Yesterday: {_moon_yesterday}')
            LOG.debug(f'Moon Today: {_moon_today}')
            LOG.debug(f'Moon Tomorrow: {_moon_tomorrow}')

            # based on the next moonset we can find its corresponding moonrise
            # moon set plus some extra needs to be in the future
            moon_sets = []
            if 'set' in _moon_yesterday:
                moon_sets.append(_moon_yesterday['set'])
            if 'set' in _moon_today:
                moon_sets.append(_moon_today['set'])
            if 'set' in _moon_tomorrow:
                moon_sets.append(_moon_tomorrow['set'])

            moon_sets.sort(reverse=False)
            LOG.debug(f'Moon sets: {moon_sets}')
            for _set in moon_sets:
                if _set + datetime.timedelta(hours=2) > datetime.datetime.now():
                    moon_set = _set
                    LOG.debug(f'Moon Set for relevant cycle is: {moon_set}')
                    break

            moon_rises = []
            if 'rise' in _moon_yesterday:
                moon_rises.append(_moon_yesterday['rise'])
            if 'rise' in _moon_today:
                moon_rises.append(_moon_today['rise'])
            if 'rise' in _moon_tomorrow:
                moon_rises.append(_moon_tomorrow['rise'])

            moon_rises.sort(reverse=True)
            LOG.debug(f'Moon rises: {moon_rises}')
            for _rise in moon_rises:
                if _rise < moon_set:
                    moon_rise = _rise
                    LOG.debug(f'Moon Rise for relevant cycle is: {moon_rise}')
                    break

            _moon = dict()
            try:
                _moon['rise'] = moon_rise

                _moon['set'] = moon_set

                decimal_moonrise = float(_moon['rise'].strftime('%H')) + float(_moon['rise'].strftime('%M')) / 60
                arc_length_moonrise = decimal_moonrise / hours * 360.0
                LOG.info(f'Moonrise: {str(_moon["rise"].strftime("%H:%M"))}')

                decimal_moonset = float(_moon['set'].strftime('%H')) + float(_moon['set'].strftime('%M')) / 60
                arc_length_moonset = decimal_moonset / hours * 360.0
                LOG.info(f'Moonset: {str(_moon["set"].strftime("%H:%M"))}')

                color = (0, 128, 255, 255)
                _size_astral = 0.20  # TODO: bigger means smaller circle
                _width = 0.012
                size_astral = [
                    (
                        round(_size * _size_astral),
                        round(_size * _size_astral)
                    ),
                    (
                        round(_size - _size * _size_astral),
                        round(_size - _size * _size_astral)
                    )
                ]
                width_astral = round(_size * _width)
                _draw_moon.arc(
                    size_astral,
                    start=arc_length_moonrise+arc_twelve,
                    end=arc_length_moonset+arc_twelve,
                    fill=color,
                    width=width_astral
                )

            except UnboundLocalError:
                LOG.exception('No Moon Rise found that happens before Moon Set:')

        # Orientation
        #   0: landscape
        #  90: portrait (90 CCW)
        # 180: reverse landscape (180 CCW)
        # 270: reverse portrait (270 CCW)
        # comp = comp.rotate(0, expand=False)

        comp = comp.resize(
            (
                round(_size/Settings.ANTIALIAS.value),
                round(_size/Settings.ANTIALIAS.value),
            ),
            Image.Resampling.LANCZOS
        )

        return comp


# ---- CLI ----


def parse_args(args):

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    # group = parser.add_mutually_exclusive_group(required=True)
    #
    # list_group = group.ad

    group_save = parser.add_argument_group("save")

    group_query = parser.add_argument_group("query")



    # group = parser.add_mutually_exclusive_group(
    #     required=True
    # )

    group_save.add_argument(
        "-a",
        "--address",
        dest="address",
        help="Set Address",
        type=str,
        required=False,
    )

    # group_save.add_argument(
    #     "-tz",
    #     "--time-zone",
    #     dest="time_zone",
    #     help="Set time zone",
    #     type=str,
    #     required=False,
    # )

    group_save.add_argument(
        "-f",
        "--out-file",
        dest="out_file",
        help="Where to save the PNG to.",
        type=pathlib.Path,
        required=False,
    )

    group_save.add_argument(
        "-i",
        "--iso",
        dest="iso",
        help="ISO timestamp like '2019-01-04T16:41:24+02:00'",
        default=None,
        type=str,
        required=False,
    )

    # group_query.add_argument(
    #     "-l",
    #     "--list-time-zone",
    #     dest="list_time_zone",
    #     help="List time zones",
    #     action="store_true",
    # )

    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    # print(args)
    args = parse_args(args)
    setup_logging(args.loglevel)
    # print(args)

    # if args.list_time_zone:
    #     from pprint import pprint
    #     pprint(zoneinfo.available_timezones())
    #     sys.exit(0)

    if args.out_file.resolve().parent.exists():
        moon_clock.MoonClock().get_clock(address=args.address, iso=args.iso).save(args.out_file)

    else:
        LOG.error(f"Destination directory does not exist: {args.out_file.parent.as_posix()}")
        sys.exit(1)

    sys.exit(0)


def run():
    main(sys.argv[1:])


if __name__ == "__main__":
    run()


