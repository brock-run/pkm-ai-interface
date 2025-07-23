#!/bin/bash
set -euo pipefail

# Simple setup script to install Docker on Ubuntu-based systems.
# Only runs if docker command is not found.

if ! command -v docker >/dev/null 2>&1; then
    echo "[setup] Installing Docker..."
    apt-get update
    apt-get install -y docker.io
fi

DOCKER_VERSION=$(docker --version 2>/dev/null || echo "not installed")

echo "[setup] Docker version: $DOCKER_VERSION"

echo "Docker installed. To build the container:" >&2
echo "  docker build -t roam-mcp-proxy ./src" >&2
