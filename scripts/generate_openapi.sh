#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
# allow overriding docs output directory for testing
DOCS_DIR="${DOCS_DIR:-$REPO_ROOT/docs}"
mkdir -p "$DOCS_DIR"

RAW_SPEC="$DOCS_DIR/roam_mcp_openapi.json"
TRIM_SPEC="$DOCS_DIR/openapi_trim.json"

# allow overriding MCP URL (default http://localhost:8088/openapi.json)
MCP_URL="${MCP_URL:-http://localhost:8088/openapi.json}"

echo "Fetching OpenAPI spec from MCP container at $MCP_URL..."
curl -sf "$MCP_URL" -o "$RAW_SPEC"

echo "Trimming spec to required endpoints..."
jq '{
  openapi: .openapi,
  info: .info,
  paths: {
    "/roam_process_batch_actions": .paths["/roam_process_batch_actions"],
    "/roam_fetch_page_by_title": .paths["/roam_fetch_page_by_title"],
    "/analytics/log": .paths["/analytics/log"]
  },
  components: .components
}' "$RAW_SPEC" > "$TRIM_SPEC"

echo "Trimmed schema written to $TRIM_SPEC"
