import datetime
from collections import OrderedDict
from itertools import groupby

from django.http import HttpResponse
from django.views.generic import View
from django.template.response import TemplateResponse

from database.models import IgStat, Accounts
from .statistic import get_stat, get_promo_stat, get_daily_stat, get_unfilled_profiles_cnt

FOLLOWERS_COUNT_CONST = 'followers_count'
FOLLOWING_COUNT_CONST = 'following_count'
SDAYS = 30


class FollowersCountChart(View):
    scope_attr = FOLLOWERS_COUNT_CONST

    def get(self, request):
        scope_attr = self.scope_attr
        stats = list(IgStat.objects.filter(
            timestamp__range=(datetime.datetime.now() - datetime.timedelta(days=SDAYS), datetime.datetime.now())
        ).values_list('account__username', 'timestamp', scope_attr).order_by('account__username', 'timestamp'))
        stats_dict = dict((k, map(lambda el: el[1:], list(i))) for k, i in groupby(stats, key=lambda s: s[0]))
        return TemplateResponse(request, 'followers_chart.html', {'stats_dict': stats_dict})


class FollowingCountChart(FollowersCountChart):
    scope_attr = FOLLOWING_COUNT_CONST


def stat(request, ig_account):
    stat_data = get_stat(ig_account)
    return HttpResponse(stat_data.replace('\n', '<br>'))


def stat_all(request):
    headers_map = OrderedDict((
        ('num', '№'),
        ('id', 'ID'),
        ('username', 'Профиль'),
        ('followers_cnt', 'Подписчиков'),
        ('following_cnt', 'Подписок'),
        ('followers_diff', 'Прирост подписчиков'),
        ('last_open_promo_type', 'Текущий процесс'),
        ('last_open_start', 'Начало процесса'),
        ('color_following_is_ok', 'Состояние фолловинга'),
        ('color_unfollowing_is_ok', 'Состояние анфолловинга'),
        ('color_liking_is_ok', 'Состояние лайкинга'),
        ('color_looking_is_ok', 'Состояние Лукинга'),
        ('follow_request_cnt', 'Подписок за 24ч'),
        ('unfollow_request_cnt', 'Отписок за 24ч'),
        ('like_request_cnt', 'Лайков за 24ч'),
        ('look_request_cnt', 'Просмотров за 24ч'),
        ('ignored_cnt', 'Игноры за 24ч'),
        ('following_total', 'Всего подписок'),
        ('unfollowing_total', 'Всего отписок'),
        ('liking_total', 'Всего лайков'),
        ('looking_total', 'Всего лайков'),
        ('ignored_total', 'Всего игноров'),
        ('last_following_date', 'Последняя подписка'),
        ('last_unfollowing_date', 'Последняя отписка'),
        ('last_liking_date', 'Последний лайк'),
        ('last_looking_date', 'Последний лайк'),
        ('last_ignored_date', 'Последний игнор'),
        ('following_queue_len', 'Очередь на фолловинг'),
        ('unfollowing_queue_len', 'Очередь на анфолловинг'),
        ('liking_queue_len', 'Очередь на лайкинг'),
        ('looking_queue_len', 'Очередь на лукинг'),
        ('proxy', 'Текущий прокси'),
        ('last_following_exc', 'Последняя ошибка фолловинга'),
        ('last_unfollowing_exc', 'Последняя ошибка анфолловинга'),
        ('last_liking_exc', 'Последняя ошибка лайкинга'),
        ('last_looking_exc', 'Последняя ошибка лукинга'),
    ))
    headers = headers_map.values()
    stats = []
    num = 0
    for account in Accounts.objects.filter(banned=False).order_by('id'):
        num += 1
        account_stat = get_promo_stat(account)
        account_stat['num'] = num
        account_stat['id'] = account.id
        account_stat['username'] = account.username
        account_stat['proxy'] = account.proxy.ip if account.proxy else ''
        account_stat['color_following_is_ok'] = '#b0f2e5' if account_stat['following_is_ok'] else '#f1afc7'
        account_stat['color_unfollowing_is_ok'] = '#b0f2e5' if account_stat['unfollowing_is_ok'] else '#f1afc7'
        account_stat['color_liking_is_ok'] = '#b0f2e5' if account_stat['liking_is_ok'] else '#f1afc7'
        account_stat['color_looking_is_ok'] = '#b0f2e5' if account_stat['looking_is_ok'] else '#f1afc7'
        for_append = []
        for key in headers_map.keys():
            for_append.append('' if account_stat[key] is None else account_stat[key])
        stats.append(for_append)
    return TemplateResponse(request, 'stat_table.html', {'headers': headers, 'stats': stats})


def daily_stat(request):
    stat = get_daily_stat(datetime.timedelta(hours=24))
    unfilled_cnt = get_unfilled_profiles_cnt()
    stat_msg = f'За последние 24ч:' \
        f'\nЗафолловлено: {stat["followed_cnt"]}' \
        f'\nРасфолловлено: {stat["unfollowed_cnt"]}' \
        f'\nЛайкано: {stat["liked_cnt"]}' \
        f'\nПросмотрено: {stat["looked_cnt"]}' \
        f'\nПодписок: {stat["followers_cnt"]}' \
        f'\nПодписчиков: {stat["following_cnt"]}' \
        f'\nПрирост подписок: {stat["followers_diff"]}' \
        f'\nНе распределено: {unfilled_cnt}'
    return HttpResponse(stat_msg.replace('\n', '<br>'))
