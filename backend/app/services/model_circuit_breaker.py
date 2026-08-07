import asyncio
import time
from enum import StrEnum


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, threshold: int = 3, reset_seconds: float = 30):
        self.threshold = threshold
        self.reset_seconds = reset_seconds
        self.failures = 0
        self.opened_at = 0.0
        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()

    async def allow(self) -> bool:
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if time.monotonic() - self.opened_at >= self.reset_seconds:
                    self.state = CircuitState.HALF_OPEN
                    return True
                return False
            return self.state != CircuitState.HALF_OPEN

    async def success(self) -> None:
        async with self._lock:
            self.failures = 0
            self.state = CircuitState.CLOSED

    async def failure(self) -> None:
        async with self._lock:
            self.failures += 1
            if self.state == CircuitState.HALF_OPEN or self.failures >= self.threshold:
                self.state = CircuitState.OPEN
                self.opened_at = time.monotonic()
