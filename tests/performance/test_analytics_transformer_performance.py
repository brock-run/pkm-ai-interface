"""Performance tests for the analytics transformer."""

import base64
import json

from src.analytics_transformer import lambda_handler


def _build_event(n=100):
    records = []
    for i in range(n):
        payload = {"id": i}
        encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        records.append({"recordId": str(i), "data": encoded})
    return {"records": records}


def test_analytics_transformer_performance(benchmark):
    """Benchmark the transformer with a larger payload."""
    event = _build_event(100)
    result = benchmark(lambda_handler, event, None)
    assert len(result["records"]) == 100
