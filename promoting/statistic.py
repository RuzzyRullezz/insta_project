import datetime

from django.utils import timezone
from pyctogram.instagram_client.web import get_user_info

from database.models import IgStat, IgLog, Accounts, Profile, Following, Liked, Looked, Ignored, PromoHistory, PromoType
from promo_bots.counters import IgLogFollowingsCounter, IgLogUnfollowingsCounter, IgLogLikeCounter, IgLogLookingCounter


def get_exception_type_from_traceback(traceback_str):
    return traceback_str.strip().split('\n')[-1].split(':')[0]


def get_promo_stat(account):
    stat_dict = {}
    last_stats = IgStat.objects.filter(
        account=account,
        timestamp__gte=timezone.now() - datetime.timedelta(days=1)
    ).order_by('timestamp')
    first_stat_followers_count = last_stats.first().followers_count if last_stats.first() else 0
    last_stat_followers_count = last_stats.last().followers_count if last_stats.last() else 0
    last_stat_following_count = last_stats.last().following_count if last_stats.last() else 0
    stat_dict['followers_cnt'] = last_stat_followers_count
    stat_dict['following_cnt'] = last_stat_following_count
    stat_dict['followers_diff'] = last_stat_followers_count - first_stat_followers_count

    stat_dict['follow_request_cnt'] = IgLogFollowingsCounter(account).count()
    stat_dict['unfollow_request_cnt'] = IgLogUnfollowingsCounter(account).count()
    stat_dict['like_request_cnt'] = IgLogLikeCounter(account).count()
    stat_dict['look_request_cnt'] = IgLogLookingCounter(account).count()

    stat_dict['ignored_cnt'] = Ignored.objects.filter(
        owner=account,
        created__gte=timezone.now() - datetime.timedelta(hours=24)
    ).count()

    stat_dict['following_total'] = Profile.objects.filter(
        owner=account, passed=True, promo_type=PromoType.following
    ).count()
    stat_dict['unfollowing_total'] = Following.objects.filter(owner=account, closed__isnull=False).count()
    stat_dict['liking_total'] = Profile.objects.filter(
        owner=account, passed=True, promo_type=PromoType.liking
    ).count()
    stat_dict['looking_total'] = Profile.objects.filter(
        owner=account, passed=True, promo_type=PromoType.looking
    ).count()

    stat_dict['ignored_total'] = Ignored.objects.filter(owner=account).count()

    last_following = Following.objects.filter(owner=account).order_by('-opened').first()
    stat_dict['last_following_date'] = last_following.opened if last_following else None

    last_unfollowing = Following.objects.filter(owner=account, closed__isnull=False).order_by('-closed').first()
    stat_dict['last_unfollowing_date'] = last_unfollowing.closed if last_unfollowing else None

    last_liking = Liked.objects.filter(owner=account).order_by('-created').first()
    stat_dict['last_liking_date'] = last_liking.created if last_liking else None

    last_looking = Looked.objects.filter(owner=account).order_by('-created').first()
    stat_dict['last_looking_date'] = last_looking.created if last_looking else None

    last_ignored = Ignored.objects.filter(owner=account).order_by('-created').first()
    stat_dict['last_ignored_date'] = last_ignored.created if last_ignored else None

    stat_dict['following_queue_len'] = Profile.objects.filter(
        owner=account, passed=False,
        promo_type=PromoType.following
    ).count()
    stat_dict['unfollowing_queue_len'] = Following.objects.filter(
        owner=account,
        opened__lte=timezone.now() - datetime.timedelta(days=3),
        status__in=(Following.Follow.code, Following.Requested.code)
    ).count()
    stat_dict['liking_queue_len'] = Profile.objects.filter(
        owner=account, passed=False,
        promo_type=PromoType.liking,
    ).count()
    stat_dict['looking_queue_len'] = Profile.objects.filter(
        owner=account, passed=False,
        promo_type=PromoType.looking,
    ).count()

    last_following_promo = PromoHistory.objects.filter(
        account=account, promo_type=PromoType.following, start__gte=timezone.now() - datetime.timedelta(days=2)
    ).order_by('-start').first()
    if last_following_promo:
        stat_dict['last_following_exc'] = get_exception_type_from_traceback(last_following_promo.traceback) if last_following_promo.traceback else None
        stat_dict['following_is_ok'] = last_following_promo.success is None or last_following_promo.success == True
    else:
        stat_dict['last_following_exc'] = None
        stat_dict['following_is_ok'] = False

    last_unfollowing_promo = PromoHistory.objects.filter(
        account=account, promo_type=PromoType.unfollowing, start__gte=timezone.now() - datetime.timedelta(days=2)
    ).order_by('-start').first()
    if last_unfollowing_promo:
        stat_dict['last_unfollowing_exc'] = get_exception_type_from_traceback(last_unfollowing_promo.traceback) if last_unfollowing_promo.traceback else None
        stat_dict['unfollowing_is_ok'] = last_unfollowing_promo.success is None or last_unfollowing_promo.success == True
    else:
        stat_dict['last_unfollowing_exc'] = None
        stat_dict['unfollowing_is_ok'] = False

    last_liking_promo = PromoHistory.objects.filter(
        account=account, promo_type=PromoType.liking, start__gte=timezone.now() - datetime.timedelta(days=2)
    ).order_by('-start').first()
    if last_liking_promo:
        stat_dict['last_liking_exc'] = get_exception_type_from_traceback(last_liking_promo.traceback) if last_liking_promo.traceback else None
        stat_dict['liking_is_ok'] = last_liking_promo.success is None or last_liking_promo.success == True
    else:
        stat_dict['last_liking_exc'] = None
        stat_dict['liking_is_ok'] = False

    last_looking_promo = PromoHistory.objects.filter(
        account=account, promo_type=PromoType.looking, start__gte=timezone.now() - datetime.timedelta(days=2)
    ).order_by('-start').first()
    if last_looking_promo:
        stat_dict['last_looking_exc'] = get_exception_type_from_traceback(last_looking_promo.traceback) if last_looking_promo.traceback else None
        stat_dict['looking_is_ok'] = last_looking_promo.success is None or last_looking_promo.success == True
    else:
        stat_dict['last_looking_exc'] = None
        stat_dict['looking_is_ok'] = False

    last_open_promo = PromoHistory.objects.filter(account=account,  end__isnull=True).order_by('-start').first()
    if last_open_promo:
        stat_dict['last_open_promo_type'] = PromoType.get_human(last_open_promo.promo_type)
        stat_dict['last_open_start'] = last_open_promo.start
    else:
        stat_dict['last_open_promo_type'] = None
        stat_dict['last_open_start'] = None
    return stat_dict


def get_ig_stat_text(username):
    user_info = get_user_info(username)
    if user_info is None:
        reply = f'Не удалость найти аккаунт {username} в IG'
    else:
        reply = f'Пользователь: {user_info["username"]}\n' \
                f'ID: {user_info["pk"]}\n' \
                f'Полное имя: {user_info["full_name"]}\n' \
                f'Открытый: {"Нет" if user_info["is_private"] else "Да"}\n' \
                f'Верифицированный: {"Да" if user_info["is_verified"] else "Нет"}\n' \
                f'Публикаций: {user_info["media_count"]}\n' \
                f'Подписчиков: {user_info["follower_count"]}\n' \
                f'Подписок: {user_info["following_count"]}\n' \
                f'Биография: {user_info["biography"]}'
    return reply


def get_promo_stat_text(username):
    account = Accounts.objects.filter(username=username).first()
    if account is None:
        reply = f'Не удалось найти аккаунт {username} в базе данных'
    else:
        reply = ''
        stat_dict = get_promo_stat(account)
        reply += f'\nПрирост подписчиков: {stat_dict["followers_diff"]}'
        reply += f'\nЗапросов на подписку за 24ч.: {stat_dict["follow_request_cnt"]}'
        reply += f'\nЗапросов на отписку за 24ч.: {stat_dict["unfollow_request_cnt"]}'
        reply += f'\nЗапросов на лайк за 24ч.: {stat_dict["like_request_cnt"]}'
        reply += f'\nПроигноривано за 24ч.: {stat_dict["ignored_cnt"]}'
        reply += f'\nЗафолловлено всего: {stat_dict["following_total"]}'
        reply += f'\nЗалайкано всего: {stat_dict["liking_total"]}'
        reply += f'\nПроигнорировано всего:  {stat_dict["ignored_total"]}'
        if stat_dict["last_following_date"]:
            reply += f'\nПоследний фолловинг: {stat_dict["last_following_date"]}'
        if stat_dict["last_liking_date"]:
            reply += f'\nПоследний лайкинг: {stat_dict["last_liking_date"]}'
        if stat_dict["last_ignored_date"]:
            reply += f'\nПоследний игнор: {stat_dict["last_ignored_date"]}'
        reply += f'\nОчередь на фолловинг: {stat_dict["following_queue_len"]}'
        reply += f'\nОчередь на лайкинг: {stat_dict["liking_queue_len"]}'
    return reply


def get_daily_stat(period):
    begin = timezone.now() - period
    sova_timofei = Accounts.objects.get(username='sova_timofei')
    ig_info = get_user_info(sova_timofei.username)
    last_stats = IgStat.objects.filter(
        account=sova_timofei,
        timestamp__gte=begin
    ).order_by('timestamp')
    first_stat_followers_count = last_stats.first().followers_count if last_stats.first() else 0
    last_stat_followers_count = last_stats.last().followers_count if last_stats.last() else 0
    daily_stat = {
        'followed_cnt': Following.objects.filter(opened__gte=begin).count(),
        'unfollowed_cnt': Following.objects.filter(closed__gte=begin).count(),
        'liked_cnt': Liked.objects.filter(created__gte=begin).count(),
        'looked_cnt': Looked.objects.filter(created__gte=begin).count(),
        'followers_cnt': ig_info['follower_count'],
        'following_cnt': ig_info['following_count'],
        'followers_diff': last_stat_followers_count - first_stat_followers_count,
    }
    return daily_stat


def get_stat(username):
    return "\n".join((get_ig_stat_text(username), get_promo_stat_text(username)))


def get_unfilled_profiles_cnt():
    return Profile.objects.filter(owner__isnull=True).count()
