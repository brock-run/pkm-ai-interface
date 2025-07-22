# pkm-ai-interface

Utility scripts and docs for working with the Roam MCP proxy.

## OpenAPI schema generation

1. Start the MCP container locally:
   ```bash
   docker run -p 8088:8088 roam-research-mcp:0.3.x
   ```
2. Run the helper script (optionally set `MCP_URL` or `DOCS_DIR`):
   ```bash
   MCP_URL=http://localhost:8088/openapi.json \
   ./scripts/generate_openapi.sh
   ```
   It fetches the schema from the container and writes a trimmed version to
   `docs/openapi_trim.json` containing only the endpoints required by the Custom GPT.

## Testing

Run the script manually and verify that `docs/openapi_trim.json` is created.
For an automated check, run:
```bash
pytest -k generate_openapi
```
