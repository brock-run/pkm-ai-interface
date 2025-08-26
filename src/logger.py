import json
import os

import boto3

firehose_client = boto3.client(
    "firehose", region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)


def log_event(data, stream_name=None, client=None):
    """Send a single analytics record to Kinesis Firehose."""
    client = client or firehose_client
    stream = stream_name or os.getenv("FIREHOSE_STREAM_NAME")
    if not stream:
        raise RuntimeError("FIREHOSE_STREAM_NAME not set")

    record = {"Data": json.dumps(data) + "\n"}
    client.put_record(DeliveryStreamName=stream, Record=record)
