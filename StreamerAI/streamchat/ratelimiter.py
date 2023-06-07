import logging
import time

logger = logging.getLogger("RateLimiter")


class RateLimiter:
    """
    Applies a window-based rate limiting mechanism
    """

    def __init__(self, window_max_count, window_length_in_seconds):
        self.window_max_count = window_max_count
        self.window_length_in_seconds = window_length_in_seconds
        self.window_start_time = time.time()
        self.window_current_count = 0
    
    def meets_limit(self):
        current_time = time.time()
        time_since_window_start = current_time - self.window_start_time

        if time_since_window_start > self.window_length_in_seconds:
            # reset window as we've moved onto the next window
            self.window_start_time = current_time
            self.window_current_count = 0

        time_remaining = self.window_start_time + self.window_length_in_seconds - current_time

        if self.window_current_count < self.window_max_count:
            self.window_current_count += 1
            logger.info(
                f"comment passed window limit starting at {self.window_start_time} with current count {self.window_current_count}, seconds remaining in window: {time_remaining}"
            )
            return True
        else:
            logger.info(
                f"comment failed window limit starting at {self.window_start_time} with current count {self.window_current_count}, seconds remaining in window: {time_remaining}"
            )
            return False