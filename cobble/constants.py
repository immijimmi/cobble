class Constants:
    # Rates must be inverted to represent how long to idle
    queue_poll_rate_hz: float = 5
    task_scheduler_poll_rate_hz: float = 0.2

    logging_timestamp_format = "[%Y-%m-%dT%H:%M:%SZ]"

    server_process_terminate_idle_s = 8
    server_process_kill_idle_s = 2
