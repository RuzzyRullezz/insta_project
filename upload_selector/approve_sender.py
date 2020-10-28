import time
from telegram_informer.bot import TgApprover

from database.models import TextContent, Accounts, OldPost, OldContentDownloadError


class ApproveSender:
    sleep = 1
    max_photo = 30
    max_wait = 2 * 60 * 60

    def __init__(self, username: str):
        self.account = Accounts.objects.get(username=username)

    def send(self):
        contents = TextContent.objects.filter(
                ignore=False, approved__isnull=True, owner=self.account, instagram_post__isnull=True,
        ).order_by('-added')[:self.max_photo]

        for for_upload in contents:
            TgApprover.approve_text_content(for_upload)
            start = time.time()
            for_upload.approved = None
            for_upload.save()
            while time.time() - start < self.max_wait:
                time.sleep(self.sleep)
                actual_text_content = TextContent.objects.get(id=for_upload.id)
                if actual_text_content.approved is None or actual_text_content.ignore:
                    continue
                elif actual_text_content.approved:
                    return
                else:
                    break
            else:
                break

        old_posts = OldPost.objects.filter(
            text_content__isnull=True, owner=self.account
        ).order_by('-like_count')[:self.max_photo]
        for old_post in old_posts:
            try:
                TgApprover.approve_old_post(old_post)
            except OldContentDownloadError:
                old_post.delete()
                continue
            start = time.time()
            while time.time() - start < self.max_wait:
                time.sleep(self.sleep)
                old_post_text_content = TextContent.objects.filter(oldpost__id=old_post.id).first()
                if old_post is None:
                    continue
                if old_post_text_content.approved is None:
                    continue
                elif old_post_text_content.approved:
                    return
                else:
                    break
            else:
                return
