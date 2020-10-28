import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=4, day=22)


dag = DAG(
    'fill_bots',
    description='Получение аккаунтов для ботов',
    schedule_interval='0 * * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(days=2),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='fill_bots_task',
    bash_command=helpers.get_python_cmd('fill_bots.py'),
    depends_on_past=False,
    dag=dag,
)
