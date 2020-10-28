import os
import time
import traceback

from pyctogram.instagram_client.web import get_instagram_id
from django.utils import timezone

from database.models import Profile, Accounts, Proxy, SourceProfile, ParsingHistory
from promo_bots.client import IgClientSwarm

sleep_time = 0


def get_profile_followers(target_username):
    target_id = get_instagram_id(target_username)
    accounts = []
    for proxy in Proxy.objects.filter(enable=True):
        account = Accounts.objects.filter(proxy=proxy).exclude(username='sova_timofei').order_by('id').last()
        if account is not None:
            accounts.append(account)
    ig_clients = [account.get_bot_client() for account in accounts]
    assert ig_clients
    swarm_client = IgClientSwarm(ig_clients, target_id)
    for profiles_pack in swarm_client.parse():
        yield profiles_pack


class NewProfileSaver:
    def __init__(self, target_username: str, skip_all_times=20):
        self.skip_all_times = skip_all_times
        self.target_username = target_username

    def save(self, skip=True):
        skipped_cnt = 0
        saved_cnt = 0
        target_id = get_instagram_id(self.target_username)
        skip_all_times_cnt = 0
        for profiles_pack in get_profile_followers(self.target_username):
            users_dict = dict(map(lambda u: (u.pop('pk'), u), profiles_pack))
            pk_set = set(users_dict.keys())
            existed = set(Profile.objects.filter(instagram_id__in=pk_set).values_list('instagram_id', flat=True))
            skipped_cnt += len(existed)
            if len(pk_set - existed) == 0:
                skip_all_times_cnt += 1
            else:
                skip_all_times_cnt = 0
            if skip and skip_all_times_cnt >= self.skip_all_times:
                break
            for new_profile_id in pk_set - existed:
                profile_data = users_dict[new_profile_id]
                profile_data.pop('profile_pic_id', None)
                profile_data.pop('has_anonymous_profile_picture', None)
                profile_data.pop('latest_reel_media', None)
                new_profile = Profile(instagram_id=new_profile_id,
                                      came_from_name=self.target_username,
                                      came_from_id=target_id,
                                      **profile_data)
                new_profile.save_async()
                saved_cnt += 1
            time.sleep(sleep_time)
        return saved_cnt, skipped_cnt


def parse_target(target: SourceProfile, skip=True):
    ph = ParsingHistory.objects.create(
        source_profile=target,
        process_id=os.getpid(),
    )
    try:
        profiles_saver = NewProfileSaver(target.username)
        saved_cnt, skipped_cnt = profiles_saver.save(skip=skip)
        ph.saved_cnt = saved_cnt
        ph.skiped_cnt = skipped_cnt
        print(f'saved cnt: {saved_cnt}, skipped_cnt: {skipped_cnt}')
    except:
        ph.traceback = traceback.format_exc()
        raise
    finally:
        ph.ended = timezone.now()
        ph.save()


def parse_all_targets():
    for profile in SourceProfile.objects.all():
        print(f'Start parsing: {profile.username}')
        parse_target(profile)


def periodic_parse():
    bound = 4000 * Accounts.objects.filter(banned=False).count()
    if Profile.objects.filter(owner__isnull=True).count() <= bound:
        parse_all_targets()
