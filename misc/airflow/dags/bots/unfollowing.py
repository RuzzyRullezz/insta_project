import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers
import bootstrap

bootstrap.setup()

from database.models import Accounts

start_date = datetime.datetime(year=2019, month=3, day=24)


def create_unfollowing_dag(username):
    dag = DAG(
        f'promo_{username}_unfollowing',
        description=f'{username}: aнфолловинг профилей',
        schedule_interval='30 * * * *',
        start_date=start_date,
        dagrun_timeout=datetime.timedelta(hours=9),
        catchup=False,
        default_args=options.dag_default_kwargs,
    )
    BashOperator(
        task_id=f'promo_{username}_unfollowing_task',
        bash_command=helpers.get_python_cmd('bots/run_unfollowing.py' + f' {username}'),
        depends_on_past=False,
        dag=dag,
    )
    return dag


for account in Accounts.objects.filter(banned=False).exclude(username='sova_timofei'):
    dag = create_unfollowing_dag(account.username)
    globals()[dag.dag_id] = dag
