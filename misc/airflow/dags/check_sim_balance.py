import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=4, day=22)


dag = DAG(
    'check_sim_balance',
    description='Проверка баланса ONLINE SIM',
    schedule_interval='0 * * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(minutes=10),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='check_sim_balance_task',
    bash_command=helpers.get_python_cmd('check_sim_balance.py'),
    depends_on_past=False,
    dag=dag,
)
