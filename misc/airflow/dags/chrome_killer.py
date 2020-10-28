import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=5, day=25)


dag = DAG(
    'chrome_killer',
    description='Убийца процессов хрома',
    schedule_interval='*/10 * * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(minutes=5),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='chrome_killer_task',
    bash_command=helpers.get_python_cmd('chrome_killer.py'),
    depends_on_past=False,
    dag=dag,
)
