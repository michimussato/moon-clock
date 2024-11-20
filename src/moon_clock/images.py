import logging
from PIL import ImageFile, Image, ImageDraw
from moon_clock.settings import Settings


LOG = logging.getLogger(__name__)
LOG.setLevel(Settings.GLOBAL_LOGGING_LEVEL.value)


ImageFile.LOAD_TRUNCATED_IMAGES = True


class Resource(object):
    """
    from moon_clock.images import Resource
    """

    @property
    def MOON_TEXUTRE(self):
        return Image.open(Settings.MOON_TEXTURE.value)

    @property
    def MOON_TEXTURE_SQUARE(self):
        return self.squareify(self.MOON_TEXUTRE).resize((448, 448))

    @staticmethod
    def squareify(image):
        assert isinstance(image, Image.Image), 'need PIL Image to squareify'

        size = image.size

        small_side = min(size)
        large_side = max(size)

        if small_side == large_side:
            return image

        orientation = 'portrait' if size[0] < size[0] else 'landscape'

        crop_total = large_side - small_side
        crop_one_side = round(int(crop_total / 2))
        crop_other_side = crop_total - crop_one_side

        if orientation == 'landscape':
            top = 0
            bottom = small_side
            left = 0 + crop_one_side
            right = large_side - crop_other_side

        elif orientation == 'portrait':
            left = 0
            right = small_side
            top = 0 + crop_one_side
            bottom = large_side - crop_other_side

        image = image.crop((left, top, right, bottom))

        return image

    @staticmethod
    def round_resize(image, corner, factor=None, fixed=None):
        """
        # Resizes an image and keeps aspect ratio. Set mywidth to the desired with in pixels.

        import PIL
        from PIL import Image

        mywidth = 300

        img = Image.open('someimage.jpg')
        wpercent = (mywidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((mywidth,hsize), PIL.Image.ANTIALIAS)
        img.save('resized.jpg')
        """
        assert isinstance(image, Image.Image), 'need PIL Image to squareify'
        assert (factor is not None and fixed is None) or (fixed is not None and factor is None)

        w, h = image.size

        if factor:
            image = image.resize((round(w * factor), round(h * factor)))
        if fixed:
            if isinstance(fixed, int):
                image = image.resize((round(fixed), round(fixed)))
            elif isinstance(fixed, tuple):
                image = image.resize((round(fixed[0]), round(fixed[1])))

        bg = image.copy()  # use copy of image as background to prevent AA artifacts
        bg.putalpha(0)

        aa = 8

        mask = Image.new('RGBA', (image.size[0]*aa, image.size[1]*aa), color=(0, 0, 0, 0))

        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), mask.size], corner*aa, fill=(0, 0, 0, 255))

        mask = mask.resize(image.size, Image.Resampling.LANCZOS)

        comp = Image.composite(image, bg, mask)

        return comp
