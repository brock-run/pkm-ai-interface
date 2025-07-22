from __future__ import annotations

import json

import boto3
from moto import mock_aws
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pytest

from src import token_loader


@mock_aws
def test_load_returns_secret_json():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    secret_name = "my/secret"
    secret_value = {"token": "abc123"}
    client.create_secret(Name=secret_name, SecretString=json.dumps(secret_value))

    result = token_loader.load(secret_name, region_name="us-east-1")

    assert result == secret_value


@mock_aws
def test_load_raises_on_missing_secret():
    with pytest.raises(token_loader.TokenLoaderError):
        token_loader.load("missing", region_name="us-east-1")


@mock_aws
def test_load_raises_on_invalid_json():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    secret_name = "bad/secret"
    client.create_secret(Name=secret_name, SecretString="not-json")

    with pytest.raises(token_loader.TokenLoaderError):
        token_loader.load(secret_name, region_name="us-east-1")
