"""
Circuit Breaker Pattern
========================
Prevents cascading failures when external services (Gemini API, MongoDB) go down.
Instead of endlessly retrying a broken dependency and timing out, the circuit
"opens" after N consecutive failures and returns fallback responses immediately.

States:
  CLOSED  → Normal operation, calls pass through
  OPEN    → Too many failures, calls are rejected instantly (returns fallback)
  HALF_OPEN → After recovery_timeout, allows ONE probe request through

Usage:
    breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

    if breaker.can_execute():
        try:
            result = await call_external_service()
            breaker.record_success()
        except Exception:
            breaker.record_failure()
            result = fallback_result
    else:
        result = fallback_result  # Circuit is OPEN, don't even try
"""

import time
import logging
from enum import Enum
from threading import Lock

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 1,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0
        self._half_open_calls = 0
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if time.time() - self._last_failure_time >= self.recovery_timeout:
                    logger.info(f"[CircuitBreaker:{self.name}] Transitioning OPEN -> HALF_OPEN")
                    self._state = CircuitState.HALF_OPEN
                    self._half_open_calls = 0
            return self._state

    def can_execute(self) -> bool:
        """Check if the circuit allows a request through."""
        current_state = self.state
        if current_state == CircuitState.CLOSED:
            return True
        elif current_state == CircuitState.HALF_OPEN:
            with self._lock:
                if self._half_open_calls < self.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
        else:  # OPEN
            return False

    def record_success(self):
        """Record a successful call. If HALF_OPEN, close the circuit."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                logger.info(f"[CircuitBreaker:{self.name}] Probe succeeded. HALF_OPEN -> CLOSED")
                self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count += 1

    def record_failure(self):
        """Record a failed call. If threshold reached, open the circuit."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                logger.warning(f"[CircuitBreaker:{self.name}] Probe failed. HALF_OPEN -> OPEN")
                self._state = CircuitState.OPEN
            elif self._failure_count >= self.failure_threshold:
                logger.warning(
                    f"[CircuitBreaker:{self.name}] Threshold reached ({self._failure_count}). CLOSED -> OPEN"
                )
                self._state = CircuitState.OPEN

    def get_stats(self) -> dict:
        """Return circuit breaker statistics for monitoring."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_seconds": self.recovery_timeout,
        }


# ── Pre-configured circuit breakers for external services ──
ai_circuit_breaker = CircuitBreaker(
    name="ai_provider",
    failure_threshold=5,      # Open after 5 consecutive failures
    recovery_timeout=60,      # Try again after 60 seconds
)

db_circuit_breaker = CircuitBreaker(
    name="mongodb",
    failure_threshold=3,      # DB failures are more critical
    recovery_timeout=30,      # Recover faster
)
