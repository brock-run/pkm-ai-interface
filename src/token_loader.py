from __future__ import annotations

import json
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class TokenLoaderError(Exception):
    """Raised when the token cannot be retrieved from Secrets Manager."""


def load(secret_name: str, region_name: str | None = None) -> Dict[str, Any]:
    """Load and return a secret from AWS Secrets Manager.

    Parameters
    ----------
    secret_name: str
        Name of the secret in AWS Secrets Manager.
    region_name: str | None
        AWS region. Uses default region if ``None``.

    Returns
    -------
    Dict[str, Any]
        Parsed JSON value stored in the secret.

    Raises
    ------
    TokenLoaderError
        If the secret cannot be fetched or parsed.
    """

    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except (ClientError, BotoCoreError) as exc:
        raise TokenLoaderError(f"Unable to fetch secret: {secret_name}") from exc

    secret_string = response.get("SecretString")
    if secret_string is None:
        raise TokenLoaderError("SecretString is empty")

    try:
        return json.loads(secret_string)
    except json.JSONDecodeError as exc:
        raise TokenLoaderError("SecretString contains invalid JSON") from exc
