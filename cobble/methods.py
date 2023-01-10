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


class LockedVar:
    """
    Lockable variable for use with python's threading module.
    Not safe for use with concurrency (e.g. multiprocessing), and should never store a mutable value
    """

    def __init__(self, value):
        self._value = value
        self._lock = Lock()

    @property
    def value(self):
        """
        Use this property when you just need to read the current value of this variable.
        Does not lock the variable, it may still be edited at any time
        """

        return self._value

    @property
    def lock(self):
        """
        Acquire this lock to ensure that the variable's value does not change
        while it is held
        """

        return self._lock

    @contextmanager
    def temporary_value(self, value):
        """
        Use this context manager to set and lock the variable's value to the provided value while
        within the enclosed block, then return it to its previous value before releasing the lock
        """

        with self._lock:
            prior_value = self._value
            self._value = value
            yield
            self._value = prior_value
