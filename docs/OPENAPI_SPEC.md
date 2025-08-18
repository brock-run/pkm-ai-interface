# OpenAPI Approach and Endpoints

This project exposes a limited subset of the Roam MCP API. We generate a trimmed OpenAPI schema that contains only the endpoints required by the Custom GPT.

## Generating the schema

Run the helper script against a running MCP container:

```bash
MCP_URL=http://localhost:8088/openapi.json ./scripts/generate_openapi.sh
```

The script downloads the full OpenAPI document, filters it down to the required paths, and writes the result to `docs/openapi_trim.json`.

## Endpoints

| Path | Method | Description |
|------|--------|-------------|
| `/roam_process_batch_actions` | `POST` | Apply a batch of write operations to the Roam graph. |
| `/roam_fetch_page_by_title` | `GET`  | Retrieve a page by its title. |
| `/analytics/log`            | `POST` | Record an analytics event. |

See `openapi_trim.json` for the machine-readable schema.
