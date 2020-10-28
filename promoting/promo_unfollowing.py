import datetime
import time

from django.utils import timezone

from database.models import Following, PromoType

from .promotion import Promotion


class UnfollowingPromo(Promotion):
    promo_type = PromoType.unfollowing
    sleep_time = 30

    def prepare_promo_objs(self, publisher):
        follow_relations_qset = Following.objects.filter(
            owner=self.account,
            opened__lte=timezone.now() - datetime.timedelta(days=3),
            status__in=(Following.Follow.code, Following.Requested.code)
        ).select_related('profile').order_by('id')
        for relation in follow_relations_qset:
            data = relation.__dict__
            data['profile_instagram_id'] = relation.profile.instagram_id
            data.pop('_state')
            publisher.send_message(data)

    def process_promo_obj(self, promo_obj_json):
        if not self.ig_client_logged_in:
            self.ig_client.login()
            self.ig_client_logged_in = True
        need_to_sleep = False
        profile_instagram_id = promo_obj_json.pop('profile_instagram_id')
        following_obj = Following(**promo_obj_json)
        relation = self.ig_client.get_relation(profile_instagram_id)
        if relation is None or 'following' not in relation or 'outgoing_request' not in relation:
            following_obj.status = Following.Deleted.code
            following_obj.closed = timezone.now()
            following_obj.save_async()
        else:
            new_status = Following.Unfollow.code if following_obj.status == Following.Follow.code else Following.Unrequested.code
            following_obj.status = new_status
            if not relation['following'] and not relation['outgoing_request']:
                following_obj.closed = timezone.now()
                following_obj.save_async()
            else:
                self.ig_client.unfollow(profile_instagram_id)
                need_to_sleep = True
                following_obj.closed = timezone.now()
                following_obj.save()
        if need_to_sleep:
            time.sleep(self.sleep_time)
