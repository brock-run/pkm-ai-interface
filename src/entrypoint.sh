#!/bin/sh
set -euo pipefail

# Optionally fetch token from AWS Secrets Manager if SECRET_ID is set
if [ -n "${SECRET_ID:-}" ]; then
    TOKEN_JSON=$(aws secretsmanager get-secret-value --secret-id "$SECRET_ID" --query SecretString --output text)
    if command -v jq >/dev/null 2>&1; then
        export ROAM_API_TOKEN=$(echo "$TOKEN_JSON" | jq -r '.ROAM_API_TOKEN')
    else
        export ROAM_API_TOKEN=$(echo "$TOKEN_JSON" | sed -n 's/.*"ROAM_API_TOKEN"[ :]\{1,2\}"\([^"]*\)".*/\1/p')
    fi
fi

# Default base URL for MCP server
export ROAM_API_BASE=${ROAM_API_BASE:-"http://0.0.0.0:8088"}

exec roam-research-mcp
