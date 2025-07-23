# pkm-ai-interface

This repository holds tests and utilities for the Roam MCP proxy proof of concept.

## Configuration

Copy `.env.example` to `.env` and provide the values for the variables below:

- `ROAM_API_BASE` – Base URL of your deployed MCP proxy
- `ROAM_API_TOKEN` – API token used for Authorization header

## Running smoke tests

The `tests/smoke/test_fetch_and_append.py` test issues a simple create-and-fetch workflow against a deployed proxy. Export the base URL of your deployment as `ROAM_API_BASE` (or load it from a `.env` file) and run:

```bash
pytest tests/smoke/test_fetch_and_append.py -k prod
```

Refer to `.taskmaster/prd.md` for the full product requirements and additional implementation notes.

