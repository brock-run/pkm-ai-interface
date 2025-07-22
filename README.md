# pkm-ai-interface

This repository contains a proof-of-concept "Roam MCP Proxy" that lets a Custom GPT securely read from and write to a shared Roam Research graph. It provides infrastructure, Lambda container code, and documentation for deploying the proxy and managing access.

## Development

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Run the unit tests:
   ```bash
   pytest
   ```
   Moto is used to mock AWS services.

3. Format and lint the code:
   ```bash
   ruff .
   black .
   ```

See [`docs/SECRET_RETRIEVAL.md`](docs/SECRET_RETRIEVAL.md) for information about the secret loader utility.

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
   
## Project Structure   
```
/infra  - infrastructure-as-code
/src    - Lambda application source
/tests  - test suites
/docs   - project documentation
```

The long-term goal is a production-ready proxy with full observability and analytics of all calls.

