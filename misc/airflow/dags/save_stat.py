import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=3, day=24)


dag = DAG(
    'save_stat',
    description='Сохранение статистики',
    schedule_interval='*/10 * * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(minutes=10),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='save_stat_task',
    bash_command=helpers.get_python_cmd('save_stat.py'),
    depends_on_past=False,
    dag=dag,
)
