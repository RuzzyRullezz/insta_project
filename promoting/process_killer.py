import os

import datetime
import signal

from django.utils import timezone
from database.models import PromoHistory, IgLog


def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def kill_frozen():
    for history in PromoHistory.objects.filter(
            success__isnull=True,
            end__isnull=True,
            start__lte=timezone.now() - datetime.timedelta(minutes=30)):
        if check_pid(history.process_id):
            if not IgLog.objects.filter(
                account=history.account,
                request_time__gte=timezone.now() - datetime.timedelta(minutes=30),
            ).exclude(
                url__icontains='/followers/'
            ).exists():
                print(f"Kill process pid = {history.process_id} for account = {history.account.username} and type = {history.promo_type}")
                os.kill(history.process_id, signal.SIGKILL)
                history.traceback = 'KILLED'
                history.end = timezone.now()
                history.success = False
                history.save()
        else:
            print(f"Can't find process with pid = {history.process_id}")
            history.end = timezone.now()
            history.success = False
            history.save()
