import datetime
import time

from django.utils import timezone
from pyctogram.instagram_client.exceptions import InstagramNotAuthorizedToView

from database.models import Profile, Following, Ignored, PromoHistory, PromoType, Liked, Looked
from .promotion import Promotion
from .exceptions import SpamUnblockWait


class LookingPromo(Promotion):
    promo_type = PromoType.looking
    sleep_time = 30

    def pre_run(self):
        ig_unblock_for_spam_wait = 24
        ig_user_unrestricted_wait = 24
        if PromoHistory.objects.filter(
            promo_type=self.promo_type,
            account=self.account,
            traceback__contains='InstagramSpamDetected',
            end__gte=timezone.now() - datetime.timedelta(hours=ig_unblock_for_spam_wait)
        ).exists():
            raise SpamUnblockWait("Wait until IG unblock spam")
        if PromoHistory.objects.filter(
            promo_type=self.promo_type,
            account=self.account,
            traceback__contains='InstagramUserRestricred',
            end__gte=timezone.now() - datetime.timedelta(hours=ig_user_unrestricted_wait)
        ).exists():
            raise SpamUnblockWait("Wait until IG unrestricted user")

    def prepare_promo_objs(self, publisher):
        for_look_qset = Profile.objects.filter(
            owner=self.account,
            passed=False,
            promo_type=self.promo_type,
        ).order_by('id')
        for profile in for_look_qset:
            data = profile.__dict__
            data.pop('_state')
            publisher.send_message(data)

    def process_promo_obj(self, promo_obj_json):
        profile = Profile(**promo_obj_json)
        if not self.ig_client_logged_in:
            self.ig_client.login()
            self.ig_client_logged_in = True
        relation = self.ig_client.get_relation(profile.instagram_id)
        if relation is None or relation['followed_by']:
            new_ignored = Ignored(
                profile_id=profile.id, owner=self.account,
                reason='Уже подписан' if relation else 'Во время лукинг не был установлен relation'
            )
            new_ignored.save_async()
            profile.passed = True
            profile.save_async()
        else:
            if relation['following'] or relation['outgoing_request']:
                # Юзеру уже был отправлен запрос на подписку, выставляем в БД
                status = Following.Follow.code if relation['following'] else Following.Requested.code
                new_following = Following(
                    owner=self.account,
                    profile_id=profile.id,
                    status=status,
                )
                new_following.save_async()
                profile.promo_type = PromoType.following
                profile.save_async()
            else:
                story_reel = self.ig_client.get_user_story_feed(profile.instagram_id)['reel']
                if story_reel:
                    items = story_reel['items']
                    mark_seen_response = self.ig_client.mark_media_seen(items)
                    status = mark_seen_response['status']
                    if status != 'ok':
                        raise RuntimeError('Look media response.status != ok.' + str(mark_seen_response))
                    Looked(
                        owner=self.account,
                        profile_id=profile.id,
                        items_ids=list(map(lambda i: i['id'], items))
                    ).save_async()
                    profile.passed = True
                    profile.save_async()
                    time.sleep(self.sleep_time)
                else:
                    # Смотрим, возможно ли достать последнюю публикацю
                    try:
                        last_media = self.ig_client.get_last_media_id(profile.instagram_id)
                        if last_media:
                            # Возможно определить id последнего поста
                            profile.promo_type = PromoType.liking
                        else:
                            profile.promo_type = PromoType.following
                    except InstagramNotAuthorizedToView:
                        new_ignored = Ignored(
                            profile_id=profile.id, owner=self.account,
                            reason='Пользователь удален или заблокирован.'
                        )
                        new_ignored.save_async()
                        profile.passed = True
                    profile.save_async()
