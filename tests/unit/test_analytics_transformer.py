import base64
import json

from src.analytics_transformer import lambda_handler


def test_transformer_enriches_event():
    payload = {"action": "test"}
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    event = {"records": [{"recordId": "1", "data": encoded}]}

    result = lambda_handler(event, None)

    assert "records" in result
    record = result["records"][0]
    assert record["recordId"] == "1"
    assert record["result"] == "Ok"

    out = json.loads(base64.b64decode(record["data"]).decode())
    assert out["action"] == "test"
    assert "processed_at" in out

