from enum import Enum


class QueueTaskKey(str, Enum):
    name = 'name'
    args = 'args'
    kwargs = 'kwargs'

    idle_after_s = 'idle_after_s'


class ScheduleEntryKey(str, Enum):
    delay_m = 'delay_m'
    task_details = 'task_details'
    is_repeating = 'is_repeating'
