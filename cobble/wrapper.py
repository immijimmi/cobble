from tkcomponents import Component

from time import sleep
from collections import deque
from typing import Dict, Optional, Any
from threading import Thread
from subprocess import Popen, PIPE
from datetime import datetime
from json import loads
from logging import info, debug, warning

from .constants import Constants
from .config import Config
from .methods import WorkingDirectory
from .enums import QueueTaskKey, ScheduleEntryKey


class Wrapper(Component):
    def __init__(self, container, config=Config):
        super().__init__(container)

        self._config = config

        self._server_process = None
        self._is_server_loaded: bool = False

        self._server_started: Optional[datetime] = None
        self._task_schedule: list = []
        self._task_queue = deque()  # Only edit this via manager methods such as `.enqueue_task()`
        self._server_output = deque()

        self._threads = []

        # Start wrapper threads
        for func in (
                self.thread_queue_handler,
                self.thread_server_output,
                self.thread_server_input,
                self.thread_task_scheduler
        ):
            debug(f"Starting new thread: {func.__name__}")
            new_thread = Thread(target=func)

            self._threads.append(new_thread)
            new_thread.start()

    @property
    def is_server_process_running(self) -> bool:
        if self._server_process is not None:
            if self._server_process.poll() is None:
                return True

        self._is_server_loaded = False
        return False

    @property
    def is_server_loaded(self) -> bool:
        if self.is_server_process_running:
            return self._is_server_loaded

        return False

    @property
    def is_server_loading(self) -> bool:
        return self.is_server_process_running and (not self.is_server_loaded)

    def thread_queue_handler(self) -> None:
        """
        Processes tasks from the task queue.

        Also responsible for starting up the server whenever it is not running, or restarting if it hangs
        for too long when starting up
        """

        while True:
            if not self.is_server_process_running:  # Server has stopped (can be either gracefully or due to a crash)
                # Clean up leftover data from previous server runtime
                self.clear_server_data()

                info("Server is not running - queueing startup...")
                self.enqueue_task(self.task_start_server.__name__)

            if self.is_server_loading:
                if (datetime.now() - self._server_started).total_seconds() >= Config.server_hang_threshold_s:
                    warning("Server has hung - killing process...")
                    self.task_kill_server()

                sleep(1/Constants.queue_poll_rate_hz)

            elif not self._task_queue:
                sleep(1/Constants.queue_poll_rate_hz)

            else:
                task_details = self._task_queue.pop()

                task = getattr(self, task_details[QueueTaskKey.name])
                task_args = task_details[QueueTaskKey.args] or ()
                task_kwargs = task_details[QueueTaskKey.kwargs] or {}
                task_idle_after_s = task_details[QueueTaskKey.idle_after_s]

                info(f"Executing task: {task.__name__}(*{task_args}, **{task_kwargs})")
                is_task_successful = task(*task_args, **task_kwargs)  # All tasks should return a boolean success value

                if is_task_successful and task_idle_after_s:
                    debug(f"Queue is idling ({task_idle_after_s}s)...")
                    sleep(task_details[QueueTaskKey.idle_after_s])

    def thread_server_input(self) -> None:
        while True:
            inp = input()

            self.enqueue_task(
                self.task_write_to_server.__name__,
                args=(inp,)
            )

    def thread_task_scheduler(self) -> None:
        while True:
            if self.is_server_process_running:
                elapsed_since_server_started_m = (datetime.now() - self._server_started).total_seconds()/60

                for schedule_entry in self._task_schedule:
                    entry_delay_m = schedule_entry[ScheduleEntryKey.delay_m]
                    entry_is_repeating = schedule_entry[ScheduleEntryKey.is_repeating]

                    times_triggered = schedule_entry.get("times_triggered", 0)
                    if (not entry_is_repeating) and times_triggered > 0:
                        continue

                    next_trigger_m = (times_triggered * entry_delay_m) + entry_delay_m
                    if elapsed_since_server_started_m >= next_trigger_m:
                        schedule_entry["times_triggered"] = times_triggered + 1
                        self.enqueue_task(**schedule_entry[ScheduleEntryKey.task_details])

            sleep(1/Constants.task_scheduler_poll_rate_hz)

    def thread_server_output(self) -> None:
        """
        Reads server output into `._server_output` for further processing.

        Also responsible for editing `._is_server_loaded` to indicate when the server has finished loading,
        based on specific output from the server
        """

        while True:
            if self.is_server_process_running:
                line = self._server_process.stdout.readline().decode('utf-8', errors='replace')

                # Check if the output indicates that the server has (pretty much) finished loading
                if ("Unloading dimension 1" in line) and (not self._is_server_loaded):
                    info("Server is online.")
                    self._is_server_loaded = True

                #self._server_output.append(line)  #####
                print(line, end='')  ##### TODO: Replace with the above line once `._server_output` is being read from

    def task_write_to_server(self, msg: str) -> bool:
        if self.is_server_process_running:
            self._server_process.stdin.write(bytes(msg + "\n", encoding='ascii'))
            self._server_process.stdin.flush()
            return True

        else:
            # This shouldn't happen, since the queue handler checks the server process is running before executing tasks
            warning("Unable to write to server (server is not running).")
            return False

    def task_start_server(self) -> bool:
        if self.is_server_process_running:
            warning("Server is already running, ignoring call to startup.")
            return False

        with WorkingDirectory.temporary(self._config.server_dir):
            self._server_started = datetime.now()
            self._server_process = Popen(
                self._config.server_startup_file,
                stdin=PIPE, stdout=PIPE
            )

        self.load_schedule()
        return True

    def task_kill_server(self) -> bool:
        """
        Ends the server process without saving
        """

        if self.is_server_process_running:
            self._server_process.kill()
            self._server_process = None  # Done to ensure that `.is_server_process_running` returns False immediately
            return True

        else:
            warning("Unable to kill server (server is not running).")
            return False

    def enqueue_task(
            self, name: str,
            args: Optional[tuple] = None, kwargs: Optional[Dict[str, Any]] = None,
            idle_after_s: float = 0
    ) -> None:
        """
        Adds a task to the task queue to be carried out as soon as possible. `name` should be the name of a
        valid task defined as a method on this class (should have a name beginning `task_`).

        `idle_after_s` represents how long (in seconds) the task handler thread should idle after completing the task
        (typically to allow the server to carry out work resulting from this task before moving onto the next one)
        """

        task_details = {
            QueueTaskKey.name: name,
            QueueTaskKey.args: args,
            QueueTaskKey.kwargs: kwargs,

            QueueTaskKey.idle_after_s: idle_after_s
        }

        self._task_queue.appendleft(task_details)

    def load_schedule(self) -> None:
        try:
            with WorkingDirectory.LOCK:
                with open(self._config.task_schedule_file, "r") as schedule_file:
                    self._task_schedule = loads(schedule_file.read())
            debug("Task schedule loaded.")

        except FileNotFoundError:
            warning(f"Unable to load task schedule (could not locate the schedule file).")

    def clear_server_data(self) -> None:
        """
        Should only be carried out when there is no server process currently running
        """

        self._server_started = None
        self._task_schedule.clear()  # Will be generated afresh when starting the server back up
        self.clear_queue()
        self._server_output.clear()
        debug("Prior server runtime data cleared.")

    def clear_queue(self) -> None:
        """
        Should only be carried out in circumstances where any queued tasks can be discarded (for example,
        when restarting the server)
        """

        debug(f"Clearing the task queue ({len(self._task_queue)} items discarded).")
        self._task_queue.clear()

    def _render(self):
        pass  ##### TODO
