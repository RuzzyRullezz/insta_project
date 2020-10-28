import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=5, day=2)


dag = DAG(
    'parse_frustrat',
    description='Парсинг Фрустрации',
    schedule_interval='0 * * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(minutes=30),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='parse_frustrat_task',
    bash_command=helpers.get_python_cmd('parse_frustrat.py'),
    depends_on_past=False,
    dag=dag,
)
