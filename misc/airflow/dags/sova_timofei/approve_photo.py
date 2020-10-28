import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

import options
import helpers

start_date = datetime.datetime(year=2019, month=3, day=23)


dag = DAG(
    'sova_timofei_approve_photo',
    description='Подтверждение публикации',
    schedule_interval='0 6,10,15,18 * * *',
    start_date=start_date,
    dagrun_timeout=datetime.timedelta(hours=3),
    catchup=False,
    default_args=options.dag_default_kwargs,
)

operator = BashOperator(
    task_id='sova_timofei_approve_photo_task',
    bash_command=helpers.get_python_cmd('sova_timofei/approve_photo.py'),
    depends_on_past=False,
    dag=dag,
)
