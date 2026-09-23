import logging
from collections import Counter

logger = logging.getLogger("ottodot.bookings")
metrics = Counter()


def increment(name: str) -> None:
    metrics[name] += 1


def snapshot() -> dict[str, int]:
    return dict(metrics)
