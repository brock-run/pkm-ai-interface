# pkm-ai-interface

Utilities and examples for integrating the Roam MCP proxy with custom
GPT Actions. The repository follows the style guidelines defined in the
[PRD](.taskmaster/prd.md).

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

See [`docs/SECRET_RETRIEVAL.md`](docs/SECRET_RETRIEVAL.md) for
information about the secret loader utility.
