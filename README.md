# PKM AI Interface

This repository contains a proof-of-concept for connecting a Custom GPT to a shared Roam Research graph through a minimal proxy. The docs folder provides an overview of the architecture and step‑by‑step deployment instructions.

## Quick Start

1. **Deploy the Proxy** – follow [docs/architecture.md](docs/architecture.md#deployment-steps) to bootstrap the repo, store your Roam API token, build the Lambda image and deploy via `sam deploy --guided`.
2. **Run Tests** – execute the smoke test to verify the proxy:
   ```bash
   pytest tests/smoke/test_fetch_and_append.py -k prod
   ```
3. **Create the Custom GPT** – import the published OpenAPI schema at `https://roam-api.$ENV.example.com/openapi.json` in the GPT builder, set the secret `Authorization: Bearer {{ROAM_API_TOKEN}}`, and share the GPT only with invited emails.

For more detail, including an architecture diagram and links to the PRD, see [docs/architecture.md](docs/architecture.md).

