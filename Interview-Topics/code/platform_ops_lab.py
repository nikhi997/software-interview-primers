"""Dependency-free drills for rollout gates, redaction, and trace propagation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ServiceWindow:
    requests: int
    errors: int
    p95_ms: int

    @property
    def error_rate(self) -> float:
        return self.errors / self.requests if self.requests else 1.0


def can_promote(
    baseline: ServiceWindow,
    canary: ServiceWindow,
    *,
    max_error_rate: float = 0.02,
    max_latency_regression: float = 1.25,
) -> tuple[bool, list[str]]:
    """Return whether a canary passes explicit reliability guardrails."""
    failures = []
    if canary.requests == 0:
        failures.append("canary has no traffic")
    if canary.error_rate > max_error_rate:
        failures.append(
            f"error rate {canary.error_rate:.2%} exceeds {max_error_rate:.2%}"
        )
    if canary.p95_ms > baseline.p95_ms * max_latency_regression:
        failures.append(
            f"p95 {canary.p95_ms}ms exceeds "
            f"{max_latency_regression:.0%} of baseline"
        )
    return not failures, failures


SENSITIVE_KEYS = {"authorization", "api_key", "password", "secret", "token"}


def redact(event: dict[str, Any]) -> dict[str, Any]:
    """Copy an event while redacting commonly sensitive fields recursively."""
    clean: dict[str, Any] = {}
    for key, value in event.items():
        if key.lower() in SENSITIVE_KEYS:
            clean[key] = "[REDACTED]"
        elif isinstance(value, dict):
            clean[key] = redact(value)
        else:
            clean[key] = value
    return clean


def outbound_headers(inbound: dict[str, str]) -> dict[str, str]:
    """Propagate trace context without forwarding credentials."""
    allowed = ("traceparent", "tracestate", "x-request-id")
    return {key: inbound[key] for key in allowed if key in inbound}


def main() -> None:
    baseline = ServiceWindow(requests=20_000, errors=100, p95_ms=240)
    canary = ServiceWindow(requests=2_000, errors=18, p95_ms=275)
    promoted, reasons = can_promote(baseline, canary)
    print("PROMOTE" if promoted else "STOP", reasons or ["guardrails pass"])

    event = {
        "message": "payment request",
        "trace_id": "abc123",
        "customer": {"id": "cust-7", "token": "do-not-export"},
    }
    print("SAFE EVENT", redact(event))

    inbound = {
        "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01",
        "x-request-id": "req-42",
        "authorization": "Bearer do-not-forward",
    }
    print("OUTBOUND", outbound_headers(inbound))


if __name__ == "__main__":
    main()
