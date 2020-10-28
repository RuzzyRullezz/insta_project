import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=4, day=3)


dag = DAG(
    'counters_cleaner',
    description='Сохранение статистики',
    schedule_interval='0 0 * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(minutes=10),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='counters_cleaner_task',
    bash_command=helpers.get_python_cmd('counters_cleaner.py'),
    depends_on_past=False,
    dag=dag,
)
