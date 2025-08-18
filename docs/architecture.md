# Architecture Overview

The service exposes a Lambda-based proxy that allows a Custom GPT to interact with a shared Roam Research graph. All traffic flows through an API Gateway and is logged for analytics.

```
+------------+     HTTPS      +---------------+      HTTPS       +------------+
|  Custom    | ----Action---> |  API Gateway  | ----Lambda-----> |   Roam     |
|   GPT      |                | (private URL) |  roam-mcp-proxy |  Graph API |
+------------+                +---------------+                 +------------+
       ^                            |  CloudWatch Logs & Metrics          ^
       |                            |                                    |
       |                            v                                    |
       |                       Kinesis Firehose                          |
       |                            | (raw JSON)                         |
       |                            v                                    |
       |                         S3 (Bronze) ----> Lakehouse ingestion    |
```

## Deployment Steps

1. **Bootstrap the Repository**
   ```bash
   mkdir roam-mcp-proxy && cd $_
   # /infra  – Terraform or AWS SAM templates
   # /src    – Lambda container code
   # /tests  – Pytest collections
   # /docs   – this guide + PRD
   ```
2. **Create & Store the Roam Secret**
   ```bash
   aws secretsmanager create-secret \
     --name roam/prod/apiToken \
     --secret-string '{"ROAM_API_TOKEN":"<token>"}'
   ```
   Give the Lambda role `secretsmanager:GetSecretValue`.
3. **Build the Lambda Image**
   ```dockerfile
   FROM public.ecr.aws/lambda/python:3.12-2025.03.11-arm64
   RUN pip install roam-research-mcp==0.3.*
   COPY entrypoint.sh ./
   CMD ["entrypoint.handler"]
   ```
4. **Deploy Infrastructure** (simplified)
   ```bash
   sam deploy --guided
   ```
5. **Generate & Publish OpenAPI Schema**
   ```bash
   docker run -p 8088:8088 roam-research-mcp:0.3.x
   curl -s http://localhost:8088/openapi.json > docs/roam_mcp_openapi.json
   aws s3 cp docs/roam_mcp_openapi.json s3://$DOC_BUCKET/api/openapi.json
   ```

## Running Tests

Smoke tests ensure that fetching and appending blocks works end to end.

```bash
pytest tests/smoke/test_fetch_and_append.py -k prod
```

## Creating the Custom GPT

1. Navigate to `https://chat.openai.com/gpts/new` and open *Configure*.
2. Import the OpenAPI schema from `https://roam-api.$ENV.example.com/openapi.json`.
3. Add the secret header `Authorization: Bearer {{ROAM_API_TOKEN}}` and store the value.
4. Share the GPT privately with invited emails only.

