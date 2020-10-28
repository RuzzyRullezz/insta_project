import bootstrap
bootstrap.setup()

from django.db import transaction

from vk_text_parser import parser

from database.models import TextContent, Accounts
from sova_timofei import username

frustrat_name = 'frustrat'


@transaction.atomic
def run():
    owner = Accounts.objects.get(username=username)
    vk_community_name = frustrat_name
    vk_parser = parser.VkTxtParser(vk_community_name)
    saved = 0
    parsed = list(vk_parser.parse())
    for text_elem in parsed:
        if TextContent.objects.filter(text=text_elem.text).exists():
            continue
        else:
            TextContent.objects.create(
                parser_name=vk_community_name,
                text=text_elem.text,
                post_id=text_elem.attr_id,
                owner=owner,
            )
            saved += 1
    print(f'Сохранено: {saved}')


if __name__ == '__main__':
    run()
