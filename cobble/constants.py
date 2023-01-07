class Constants:
    # Rates must be inverted to represent how long to idle
    queue_poll_rate_hz: float = 10
    task_scheduler_poll_rate_hz: float = 0.2

    logging_timestamp_format = "[%Y-%m-%dT%H:%M:%SZ]"
