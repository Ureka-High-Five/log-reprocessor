import time
import math

def exponential_decay_weight(original_weight: float, event_timestamp_ms: int, lambda_: float = 0.1) -> float:
    current_timestamp_ms = int(time.time() * 1000)
    delta_ms = current_timestamp_ms - event_timestamp_ms
    delta_days = delta_ms / (1000 * 60 * 60 * 24)

    decayed_weight = original_weight * math.exp(-lambda_ * delta_days)
    return round(decayed_weight, 2)
