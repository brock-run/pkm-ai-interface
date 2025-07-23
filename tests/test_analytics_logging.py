import os
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")

import json
from datetime import datetime, timezone
from typing import Any, Dict

import boto3
from botocore.stub import Stubber

from src import handler, logger


def _sample_event() -> Dict[str, Any]:
    return {
        "rawPath": "/analytics/log",
        "body": json.dumps({"action": "test"}),
        "requestContext": {
            "http": {"method": "POST"},
            "authorizer": {"claims": {"sub": "user123"}},
        },
    }


def test_lambda_logs_to_firehose(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv("FIREHOSE_STREAM_NAME", "stream")

    client = boto3.client("firehose", region_name="us-east-1")
    stubber = Stubber(client)
    monkeypatch.setattr(logger, "firehose_client", client)

    fixed_time = datetime(2020, 1, 1, tzinfo=timezone.utc)

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_time

    monkeypatch.setattr(handler, "datetime", FixedDatetime)

    expected_payload = {
        "user_id": "user123",
        "timestamp": fixed_time.isoformat(),
        "payload": {"action": "test"},
    }
    expected_params = {
        "DeliveryStreamName": "stream",
        "Record": {"Data": json.dumps(expected_payload) + "\n"},
    }
    stubber.add_response("put_record", {"RecordId": "1"}, expected_params)

    with stubber:
        event = _sample_event()
        resp = handler.lambda_handler(event, None)

    assert resp["statusCode"] == 200
    stubber.assert_no_pending_responses()
