import time
from threading import Lock
from collections import defaultdict
from fastapi import HTTPException, status

class InMemoryRateLimiter:
    """
    Thread-safe, in-memory sliding-window rate limiter.

    NOTE ON ARCHITECTURE:
    This rate limiter operates in-memory on the active application process.
    For horizontally scaled, multi-instance production deployments, this component
    should be backed by a centralized distributed store (e.g., Redis via Redis token bucket).
    For the current single-process architecture, this in-memory implementation provides
    effective abuse mitigation without introducing heavyweight external infrastructure dependencies.
    """
    def __init__(self, max_requests: int = 10, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history = defaultdict(list)
        self._lock = Lock()

    def check_rate_limit(self, key: str) -> None:
        """
        Records an attempt for `key` and raises HTTP 429 if the request limit is exceeded.
        """
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            timestamps = self._history[key]
            # Discard timestamps outside the sliding window
            valid_timestamps = [ts for ts in timestamps if ts > cutoff]
            if len(valid_timestamps) >= self.max_requests:
                earliest = valid_timestamps[0]
                retry_after = max(1, int(self.window_seconds - (now - earliest)))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: Maximum {self.max_requests} explanation requests per minute. Retry in {retry_after}s.",
                    headers={"Retry-After": str(retry_after)}
                )
            valid_timestamps.append(now)
            self._history[key] = valid_timestamps

    def reset(self) -> None:
        """Utility method to reset history during tests."""
        with self._lock:
            self._history.clear()

# Global rate limiter instance for Groq explanation calls: 10 requests per 60 seconds per user
explain_rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60.0)
