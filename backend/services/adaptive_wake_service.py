"""Adaptive wake timeout based on historical wake duration."""


def effective_wake_timeout(device, max_wait=None):
    """Return wake wait timeout, extended when historical data suggests longer boot times."""
    if max_wait is not None:
        return max_wait

    configured = device.wake_timeout_seconds or 120
    last_duration = device.last_wake_duration_seconds
    if not last_duration:
        return configured

    adaptive = int(last_duration * 1.5) + 15
    return min(max(configured, adaptive), 600)
