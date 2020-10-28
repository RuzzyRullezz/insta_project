import datetime
import time

from django.utils import timezone
from pyctogram.instagram_client.exceptions import InstagramCannotLikeMedia, InstagramNotAuthorizedToView

from database.models import Profile, Following, Ignored, PromoHistory, PromoType, Liked
from .promotion import Promotion
from .exceptions import SpamUnblockWait


class LikingPromo(Promotion):
    promo_type = PromoType.liking
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
        for_like_qset = Profile.objects.filter(
            owner=self.account,
            passed=False,
            promo_type=PromoType.liking,
        ).order_by('id')
        for profile in for_like_qset:
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
                reason='Уже подписан' if relation else 'Во время лайкинга не был установлен relation'
            )
            new_ignored.save_async()
            profile.passed = True
            profile.save_async()
        else:
            if relation['following'] or relation['outgoing_request']:
                # Юзеру уже был отправлен запрос на подписку, выставляем в БД
                status = Following.Follow.code if relation['following'] else Following.Requested.code
                new_liking = Following(
                    owner=self.account,
                    profile_id=profile.id,
                    status=status,
                )
                new_liking.save_async()
                profile.promo_type = PromoType.following
                profile.save_async()
            else:
                # Находим последний выложенный пост
                try:
                    last_media = self.ig_client.get_last_media_id(profile.instagram_id)
                except InstagramNotAuthorizedToView:
                    new_ignored = Ignored(
                        profile_id=profile.id, owner=self.account,
                        reason='Пользователь удален или заблокирован.'
                    )
                    new_ignored.save_async()
                    profile.passed = True
                    profile.save_async()
                else:
                    if last_media is None:
                        # Не удалось определить id последнего поста
                        profile.promo_type = PromoType.following
                        profile.save_async()
                    else:
                        try:
                            self.ig_client.like(last_media['id'])
                        except InstagramCannotLikeMedia:
                            profile.promo_type = PromoType.following
                            profile.save_async()
                        else:
                            new_liking = Liked(
                                owner=self.account,
                                profile_id=profile.id,
                                picture_id=last_media['id'],
                            )
                            new_liking.save_async()
                            profile.passed = True
                            profile.save_async()
                            time.sleep(self.sleep_time)
