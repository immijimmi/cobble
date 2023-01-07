from threading import Lock
from typing import Optional
from os import chdir, getcwd
from contextlib import contextmanager


class WorkingDirectory:
    LOCK = Lock()  # Guarantees no other threads have changed the working directory as long as this lock is held

    @classmethod
    @contextmanager
    def temporary(cls, target_dir: Optional[str] = None):
        with cls.LOCK:
            cwd = getcwd()
            if target_dir:
                chdir(target_dir)
            yield
            if target_dir:
                chdir(cwd)
