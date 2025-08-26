"""Contract tests for the analytics transformer."""

import base64
import json

from src.analytics_transformer import lambda_handler


def test_firehose_transformation_contract():
    """Ensure Firehose transformer output matches expected schema."""
    payload = {"action": "contract"}
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    event = {"records": [{"recordId": "1", "data": encoded}]}

    result = lambda_handler(event, None)

    assert "records" in result
    assert len(result["records"]) == 1
    record = result["records"][0]
    # contract: record contains id, result status, and data
    assert set(record.keys()) == {"recordId", "result", "data"}
    assert record["recordId"] == "1"
    assert record["result"] == "Ok"

    decoded = json.loads(base64.b64decode(record["data"]).decode())
    assert decoded["action"] == "contract"
    assert "processed_at" in decoded
