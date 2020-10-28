import time

from filelock import FileLock

flock = FileLock('/tmp/filelock.lock')
print(flock.is_locked)
with flock:
    print("SLEEP BEGIN")
    time.sleep(30)
    print("SLEEP END")
