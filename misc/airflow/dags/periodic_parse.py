import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=4, day=29)


dag = DAG(
    'periodic_parse',
    description='Периодический парсинг акканунтов',
    schedule_interval='0 0 * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(days=7),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='periodic_parse_task',
    bash_command=helpers.get_python_cmd('periodic_parse.py'),
    depends_on_past=False,
    dag=dag,
)
