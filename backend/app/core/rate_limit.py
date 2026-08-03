"""In-memory sliding-window rate limiter.

A lightweight, dependency-free rate limiter keyed by client IP. For local
single-process deployments this is sufficient; a Redis-backed limiter would
be the production upgrade.
"""

import threading
import time
from collections import defaultdict, deque
from typing import Deque

from app.config import settings


class RateLimiter:
    """Sliding window rate limiter using a deque of timestamps per key."""

    def __init__(
        self,
        max_requests: int | None = None,
        window_seconds: int | None = None,
    ) -> None:
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        self._buckets: dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        """Check whether ``key`` may make a request now; records it if allowed."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                return False
            bucket.append(now)
            return True

    def remaining(self, key: str) -> int:
        """Return how many requests remain for ``key`` in the current window."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            return max(0, self.max_requests - len(bucket))


rate_limiter = RateLimiter()
