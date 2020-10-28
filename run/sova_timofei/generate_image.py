import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), os.path.pardir))
import bootstrap
bootstrap.setup()

from painter.sova_timofei import SovaTimofeiPainter


def generate_image(text, post_id):
    image_path = SovaTimofeiPainter().draw_picture(text, post_id + '.jpg')
    return image_path


if __name__ == '__main__':
    text = 'Ребятки, всем привет!\nЖдите новые посты.\nА пока почитайте советы от\n\n@OLYA.WELL\n\nРекомендую =)'
    post_id = 'advert_1'
    print(generate_image(text, post_id))

