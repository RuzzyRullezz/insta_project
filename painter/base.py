import os
import textwrap

from PIL import Image, ImageDraw, ImageFont


class MaxHeightException(BaseException):
    pass


MAX_W, MAX_H = 650, 650


class Painter(object):
    def __init__(self, background_path, font_path, color):
        self.background_path = background_path
        self.font_path = font_path
        self.color = color

    def draw_picture(self, text, output):
        current_h, pad = 150, 8
        im = Image.open(self.background_path)
        font = ImageFont.truetype(self.font_path, 45)
        draw = ImageDraw.Draw(im)
        for line in text.splitlines():
            para = textwrap.wrap(line, width=28, replace_whitespace=False)
            for lline in para:
                w, h = draw.textsize(lline, font=font)
                draw.text(((MAX_W - w) / 2, current_h), lline, self.color, font=font)
                current_h += h + pad
                if current_h > MAX_H:
                    raise MaxHeightException()
        im = im.convert('RGB')
        im.save(output)
        return os.path.abspath(output)
