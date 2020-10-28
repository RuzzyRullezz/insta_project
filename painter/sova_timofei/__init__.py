import os

from django.conf import settings

from painter import Painter


class SovaTimofeiPainter(Painter):
    def __init__(self):
        background = os.path.join(os.path.dirname(__file__), 'assets', 'background.png')
        font = os.path.join(os.path.dirname(__file__), 'assets', 'text_font.ttf')
        color = (0, 0, 0)
        self.output_dir = os.path.join(settings.IMAGES_DIR, 'sova_timofei')
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)
        super().__init__(background, font, color)

    def draw_picture(self, text, filename):
        output_path = os.path.join(self.output_dir, filename)
        return super().draw_picture(text, output_path)
