from database.models import Accounts, Profile, PromoType

FOLLOWING_LOWER_BOUND = 500
LIKING_LOWER_BOUND = 500

FOLLOWING_BATCH_SIZE = 2000
LIKING_BATCH_SIZE = 2000


def append(account: Accounts):
    append_for_following = 0
    append_for_liking = 0

    if Profile.objects.filter(
        owner=account,
        passed=False,
        promo_type=PromoType.following
    ).count() <= FOLLOWING_LOWER_BOUND:
        inner_q = Profile.objects.filter(
            owner=account,
            passed=False,
            promo_type__isnull=True,
        ).values_list('pk', flat=True)[:FOLLOWING_BATCH_SIZE]
        updated = Profile.objects.filter(pk__in=inner_q).update(promo_type=PromoType.following)
        if updated == 0:
            raise RuntimeError("Can't find profile for update for following")
        append_for_following = updated

    return append_for_following, append_for_liking
