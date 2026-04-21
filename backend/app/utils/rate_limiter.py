import time
from collections import deque
from functools import wraps


class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def acquire(self):
        now = time.time()
        # Remove calls older than the period
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()

        if len(self.calls) >= self.max_calls:
            # Sleep until the oldest call expires
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
            # After sleeping, remove expired calls and try again
            return self.acquire()

        self.calls.append(time.time())
        return True


class TTLCache:
    def __init__(self, ttl_seconds: int = 30):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        entry = self.cache.get(key)
        if entry and time.time() - entry["ts"] < self.ttl:
            return entry["data"]
        return None

    def set(self, key, data):
        self.cache[key] = {"ts": time.time(), "data": data}

    def clear(self):
        self.cache.clear()


# Global rate limiter: 5 calls per 60 seconds
itick_rate_limiter = RateLimiter(max_calls=5, period=60.0)