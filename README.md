# pkm-ai-interface

This repository contains a minimal AWS Lambda application used as a proof of
concept for the Roam MCP proxy. The function exposes an `/analytics/log`
endpoint that records structured events to Amazon Kinesis Firehose.

## Usage

The Lambda expects the environment variable `FIREHOSE_STREAM_NAME` to be set to
the name of the delivery stream. Requests should include a valid Cognito
`sub` claim which is used as the `user_id` for analytics.

```
POST /analytics/log
{
  "action": "test"
}
```

A `timestamp` is added server-side and the record is forwarded to Firehose.

## Development

Install dependencies and run tests with `pytest`:

```
pip install boto3 moto[firehose]
pytest
```

## TODO

Unit tests currently stub the Firehose client. Future work includes:

- Add integration tests against a real Firehose endpoint or moto-based mock.
- Expand IAM policies and Terraform to support production deployment.
- Remove dummy credentials and use environment-specific configuration.
