import datetime
import time

from django.utils import timezone

from database.models import Profile, Following, Ignored, PromoHistory, PromoType
from .promotion import Promotion
from .exceptions import ChangeFriendshipWait, SpamUnblockWait


class FollowingPromo(Promotion):
    promo_type = PromoType.following
    sleep_time = 40

    def pre_run(self):
        ig_change_status_wait = 12  # hours
        ig_unblock_for_spam_wait = 12
        ig_user_unrestricted_wait = 12
        if PromoHistory.objects.filter(
            promo_type=self.promo_type,
            account=self.account,
            traceback__contains='IgDidntChangeStatus',
            end__gte=timezone.now() - datetime.timedelta(hours=ig_change_status_wait)
        ).exists():
            raise ChangeFriendshipWait("Wait until IG allow to change the friendship status")
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
        for_follow_qset = Profile.objects.filter(
            owner=self.account,
            passed=False,
            promo_type=PromoType.following,
        ).order_by('id')
        for profile in for_follow_qset:
            data = profile.__dict__
            data.pop('_state')
            publisher.send_message(data)

    def process_promo_obj(self, promo_obj_json):
        profile = Profile(**promo_obj_json)
        if not self.ig_client_logged_in:
            self.ig_client.login()
            self.ig_client_logged_in = True
        need_to_sleep = False
        relation = self.ig_client.get_relation(profile.instagram_id)
        if relation is None or relation['followed_by']:
            new_ignored = Ignored(
                profile_id=profile.id, owner=self.account,
                reason='Уже подписан' if relation else 'Во время фолловинга не был установлен relation'
            )
            new_ignored.save_async()
        else:
            if relation['following'] or relation['outgoing_request']:
                status = Following.Follow.code if relation['following'] else Following.Requested.code
                new_following = Following(
                    owner=self.account,
                    profile_id=profile.id,
                    status=status,
                )
                new_following.save_async()
            else:
                friendship_status = self.ig_client.follow(profile.instagram_id)['friendship_status']
                if friendship_status['following']:
                    status = Following.Follow.code
                elif friendship_status['outgoing_request']:
                    status = Following.Requested.code
                else:
                    raise RuntimeError("Unreachable statement")
                need_to_sleep = True
                new_following = Following(
                    owner=self.account,
                    profile_id=profile.id,
                    status=status,
                )
                new_following.save_async()
        profile.passed = True
        profile.save_async()
        if need_to_sleep:
            time.sleep(self.sleep_time)
