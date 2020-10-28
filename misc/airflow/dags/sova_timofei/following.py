import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=3, day=24)


dag = DAG(
    'sova_timofei_following',
    description='Фолловинг профилей',
    schedule_interval='0 * * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(hours=12),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='sova_following_task',
    bash_command=helpers.get_python_cmd('sova_timofei/run_following.py'),
    depends_on_past=False,
    dag=dag,
)
