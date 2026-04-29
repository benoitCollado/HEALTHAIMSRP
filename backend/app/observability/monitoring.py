import threading
import time
from collections import defaultdict


class _Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.start_time: float = time.time()
        self.requests_total: int = 0
        self.errors_total: int = 0
        self._durations: list[float] = []
        self.requests_by_route: dict[str, int] = defaultdict(int)

    def record(self, route: str, duration_ms: float, status_code: int) -> None:
        with self._lock:
            self.requests_total += 1
            self._durations.append(duration_ms)
            self.requests_by_route[route] += 1
            if status_code >= 500:
                self.errors_total += 1

    def snapshot(self) -> dict:
        with self._lock:
            durations = self._durations
            avg = round(sum(durations) / len(durations), 2) if durations else 0.0
            return {
                "uptime_seconds": round(time.time() - self.start_time),
                "requests_total": self.requests_total,
                "errors_total": self.errors_total,
                "avg_duration_ms": avg,
                "requests_by_route": dict(self.requests_by_route),
            }

    def reset(self) -> None:
        """Used by tests only."""
        with self._lock:
            self.requests_total = 0
            self.errors_total = 0
            self._durations.clear()
            self.requests_by_route.clear()
            self.start_time = time.time()


metrics = _Metrics()
