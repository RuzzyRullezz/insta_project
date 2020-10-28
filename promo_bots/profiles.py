from django.db.models import Count, Q
from filelock import Timeout, FileLock

from database.models import Accounts, Profile, PromoType

limit = 10000
profiles_cnt_low_bound = 2000


def get_new_profiles(account: Accounts, promo_type):
    profiles_cnt = Profile.objects.filter(
        passed=False,
        promo_type=promo_type,
        owner=account,
    ).count()
    if profiles_cnt <= profiles_cnt_low_bound:
        ids_for_update = Profile.objects.filter(
            Q(owner__isnull=True) & Q(Q(promo_type__isnull=True) | Q(promo_type=promo_type))
        ).order_by('id').values_list('id', flat=True)[:limit]
        if len(ids_for_update) < limit:
            RuntimeError("Not enough profiles")
        Profile.objects.filter(id__in=ids_for_update).update(owner=account, promo_type=promo_type)


def get_new_following_profiles(account: Accounts):
    get_new_profiles(account, PromoType.following)


def get_new_liking_profiles(account: Accounts):
    get_new_profiles(account, PromoType.liking)


def get_new_looking_profiles(account: Accounts):
    get_new_profiles(account, PromoType.looking)


def get_new_promo_profiles(account: Accounts):
    lock_file_pattern = '/tmp/parse_%d.lock'
    try:
        with FileLock(lock_file_pattern % account.id, timeout=0):
            get_new_following_profiles(account)
            get_new_liking_profiles(account)
            get_new_looking_profiles(account)
    except Timeout:
        pass


def fill_bots():
    for account in Accounts.objects.filter(banned=False):
        get_new_promo_profiles(account)
