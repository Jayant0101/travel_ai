import circuit_breaker as cb_module
from circuit_breaker import CircuitBreaker, CircuitState


def test_circuit_breaker_opens_after_threshold_failures():
    breaker = CircuitBreaker(name="test", failure_threshold=2, recovery_timeout=30)

    breaker.record_failure()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.can_execute() is True

    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    assert breaker.can_execute() is False


def test_open_transitions_to_half_open_after_timeout(monkeypatch):
    fake_time = [1000.0]
    monkeypatch.setattr(cb_module.time, "time", lambda: fake_time[0])

    breaker = CircuitBreaker(name="test", failure_threshold=1, recovery_timeout=10, half_open_max_calls=1)
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN

    fake_time[0] += 11.0
    assert breaker.state == CircuitState.HALF_OPEN
    assert breaker.can_execute() is True
    assert breaker.can_execute() is False


def test_half_open_success_closes_circuit(monkeypatch):
    fake_time = [2000.0]
    monkeypatch.setattr(cb_module.time, "time", lambda: fake_time[0])

    breaker = CircuitBreaker(name="test", failure_threshold=1, recovery_timeout=5, half_open_max_calls=1)
    breaker.record_failure()
    fake_time[0] += 6.0

    assert breaker.state == CircuitState.HALF_OPEN
    assert breaker.can_execute() is True

    breaker.record_success()
    assert breaker.state == CircuitState.CLOSED
    assert breaker.can_execute() is True
