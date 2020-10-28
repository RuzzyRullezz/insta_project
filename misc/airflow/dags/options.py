from datetime import datetime

default_start_date = datetime.utcnow().replace(
    hour=0,
    minute=0,
    second=0,
    microsecond=0
)

dag_default_kwargs = dict(
    depends_on_past=False,
)
