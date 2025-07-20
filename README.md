# pkm-ai-interface

This repository contains a proof-of-concept proxy for Roam Research built around the `roam-research-mcp` package.

## Development

1. Run `scripts/setup.sh` to install Docker (requires sudo privileges).
2. Build the Lambda container image:
   ```
   docker build -t roam-mcp-proxy ./src
   ```
3. Optional: run the container locally (requires Docker daemon):
   ```
   docker run --rm -p 9000:8080 roam-mcp-proxy
   ```
