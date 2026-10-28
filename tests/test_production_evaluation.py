import pytest
import numpy as np
from api.production_evaluation import calculate_percentiles

def test_calculate_percentiles():
    # Empty list
    assert calculate_percentiles([]) == (0.0, 0.0, 0.0)

    # Single element
    assert calculate_percentiles([10.0]) == (10.0, 10.0, 10.0)

    # Ordered elements
    latencies = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    p50, p95, p99 = calculate_percentiles(latencies)
    assert p50 == np.percentile(latencies, 50)
    assert p95 == np.percentile(latencies, 95)
    assert p99 == np.percentile(latencies, 99)

    # Real-world-like latencies
    latencies = [100.0, 110.0, 95.0, 105.0, 300.0, 102.0, 150.0, 100.0, 98.0, 112.0]
    p50, p95, p99 = calculate_percentiles(latencies)
    assert p50 == np.percentile(latencies, 50)
    assert p95 == np.percentile(latencies, 95)
    assert p99 == np.percentile(latencies, 99)
