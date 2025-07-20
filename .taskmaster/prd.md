# Roam MCP Proxy POC – PRD

> **Purpose**   Deliver a minimal yet production-grade proof-of-concept that lets a Custom OpenAI GPT read/write a shared Roam Research graph through a secure middle-layer running `roam-research-mcp`, with full observability and a clear path toward the long-term Lakehouse architecture.

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Reference Architecture](#2-reference-architecture)
3. [Step-by-Step Implementation Guide](#3-step-by-step-implementation-guide)
4. [AWS IaC Snippets](#4-aws-iac-snippets)
5. [Testing Strategy](#5-testing-strategy)
6. [Coding & Style Guidelines](#6-coding--style-guidelines)
7. [Operational Excellence & Error Handling](#7-operational-excellence--error-handling)
8. [Security & Access Control](#8-security--access-control)
9. [Post-POC Future-Ready Extensions](#9-post-poc-future-ready-extensions)
10. [Additional Information](#10-prdmd-cursor--taskmaster-mcp)

---

## 1  High-Level Overview

| Item                 | Description                                                                                                                                                                                                                               |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Goal**             | Enable Brock and Partner to converse with a Custom GPT that can read pages, search blocks, and append content to their **shared** Roam Research graph while capturing every call for analytics.                                           |
| **Why MCP?**         | `roam-research-mcp` already encapsulates batching, markdown ↔ Datalog translation, and streaming responses—perfect as a proxy.                                                                                                            |
| **Success Criteria** | **📗 Round-trip < 5 s latency** for `fetch_page` & `append_block` • **📗 100 % test-suite pass-rate** (see §5) • **📗 All API calls logged** to S3 and queryable via Athena/Iceberg • **📗 GPT accessible only to two whitelisted users** |

---

## 2  Reference Architecture

```
┌──────────┐       HTTPS         ┌──────────────┐        HTTPS         ┌──────────────┐
│ Custom   │ ───── Action ─────▶ │ API Gateway  │ ───── Lambda ───────▶ │ Roam Graph   │
│ GPT      │                    │ (private URL)│  "roam-mcp-proxy"    │  API         │
└──────────┘                    └──────────────┘                       └──────────────┘
       ▲                                 │                                     ▲
       │                                 │ CloudWatch Logs & Metrics           │
       │                                 ▼                                     │
       │                         Kinesis Firehose                              │
       │                                 │ (raw JSON)                          │
       │                                 ▼                                     │
       │                              S3 (Bronze) —▶ Lakehouse ingestion (Dagster)
```

1. **Custom GPT** – uses two Actions (`/roam` and `/analytics/log`).
2. **API Gateway (HTTP API)** – exposes a private URL; front-door for the proxy.
3. **Lambda `roam-mcp-proxy`** – Docker container (128 MB, Python 3.12) running `roam-research-mcp`.
4. **AWS Secrets Manager** – stores the Roam API token (rotated quarterly).
5. **Amazon Cognito User Pool** – authenticates Brock & Partner; authorizer injects user claims into requests.

---

## 3  Step-by-Step Implementation Guide

> All shell commands assume **AWS CLI v2** and **Docker** are installed. Replace `$ENV` placeholders as needed.

### 3.1  Repository Bootstrap

```bash
mkdir roam-mcp-proxy && cd $_
# /infra  – Terraform or AWS SAM templates
# /src    – Lambda container code (Dockerfile, entrypoint.sh)
# /tests  – Pytest / Postman collections
# /docs   – this guide + PRD
```

### 3.2  Create & Store Roam Secret

```bash
aws secretsmanager create-secret \
  --name roam/prod/apiToken \
  --secret-string '{"ROAM_API_TOKEN":"<token-from-roam-settings>"}'
```

Give the Lambda role `secretsmanager:GetSecretValue`.

### 3.3  Dockerfile (Graviton 2, arm64)

```dockerfile
FROM public.ecr.aws/lambda/python:3.12-2025.03.11-arm64

RUN pip install roam-research-mcp==0.3.*

# entrypoint.sh sets env vars then starts MCP server
COPY entrypoint.sh ./

CMD ["entrypoint.handler"]
```

### 3.4  Infrastructure-as-Code highlights (full snippet in §4)

* **iam.tf** – least-privilege role for Secrets, CloudWatch Logs, Firehose.
* **lambda.tf** – container image Lambda, 128 MB, timeout 15 s.
* **apigw\.tf** – HTTP API + custom domain `roam-api.$ENV.example.com`.
* **cognito.tf** – user pool with two users; Lambda authorizer.

### 3.5  Generate & Publish OpenAPI Schema

```bash
# Run MCP locally
docker run -p 8088:8088 roam-research-mcp:0.3.x

curl -s http://localhost:8088/openapi.json > docs/roam_mcp_openapi.json

# (Optional) Trim to three endpoints with jq
jq '{ ... }' docs/roam_mcp_openapi.json > docs/openapi_trim.json

aws s3 cp docs/openapi_trim.json s3://$DOC_BUCKET/api/openapi.json
```

### 3.6  Create the Custom GPT

1. Go to **chat.openai.com/gpts/new** → *Configure*.
2. **Actions → Import OpenAPI** → `https://roam-api.$ENV.example.com/openapi.json`.
3. Add secret header: `Authorization: Bearer {{ROAM_API_TOKEN}}` and store secret value.
4. Share GPT link privately; *Who can use* → **Only invited emails** (add Partner).

### 3.7  Analytics Logging Endpoint

* `POST /analytics/log` → API Gateway → **Kinesis Firehose** → S3 `raw/gpt_roam_logs/`.
* Transformation Lambda enriches each record with user ID (`sub`) and ISO-8601 timestamp.

### 3.8  CI/CD

* GitHub → AWS CodeBuild → `sam deploy --guided`.
* `main` → prod stack; PRs create preview stacks with suffix.

### 3.9  Smoke Test

```bash
pytest tests/smoke/test_fetch_and_append.py -k prod
# Expects HTTP 200 and block added to Roam
```

---

## 4  AWS IaC Snippets

```hcl
module "roam_mcp_proxy" {
  source         = "terraform-aws-modules/lambda/aws"
  function_name  = "roam-mcp-proxy-${var.env}"
  image_uri      = docker_registry_image.roam_mcp.image_uri
  memory_size    = 128
  timeout        = 15

  attach_policy_json = true
  policy_json = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["secretsmanager:GetSecretValue"],
        Resource = aws_secretsmanager_secret.roam_api_token.arn
      },
      {
        Effect   = "Allow",
        Action   = ["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}
```

```python
# tests/smoke/test_fetch_and_append.py
import os, requests, uuid

BASE = os.getenv("ROAM_API_BASE")

def test_fetch_and_append():
    title = "TestPage-" + uuid.uuid4().hex[:6]

    # 1) create page
    r = requests.post(
        f"{BASE}/roam_process_batch_actions",
        json={"actions":[{"create_page":{"title":title}}]}
    )
    assert r.status_code == 200

    # 2) fetch page back
    page = requests.get(
        f"{BASE}/roam_fetch_page_by_title",
        params={"title": title}
    )
    assert page.json()["title"] == title
```

---

## 5  Testing Strategy

| Layer           | Tool / Framework    | What we verify                        |
| --------------- | ------------------- | ------------------------------------- |
| **Unit**        | Pytest + moto       | Token loader, Lambda handler branches |
| **Contract**    | Postman Collections | OpenAPI schema conformance            |
| **Integration** | Pytest smoke tests  | End-to-end `fetch → append`           |
| **Security**    | AWS Prowler (CIS)   | IAM least-privilege, public S3 checks |
| **Performance** | Artillery           | p95 latency < 1 s under 10 req/s      |

---

## 6  Coding & Style Guidelines

* **Python 3.12** – lint with `ruff`, format with `black` (line length = 88).
* Return errors as [RFC 7807 problem-detail](https://opensource.zalando.com/problem/schema.yaml).
* Keep Lambda cold-start < 350 ms by pinning deps:

  ```bash
  pip install --no-binary :all: datascript==0.19.*
  ```

---

## 7  Operational Excellence & Error Handling

* Global `try/except` → HTTP 500 JSON problem doc; client retries with exponential back-off.
* CloudWatch Alarm: ≥ 5 `5xx` per minute triggers PagerDuty.
* Structured logs: `level`, `aws_request_id`, `user_id`, `tool`, `elapsed_ms`.

---

## 8  Security & Access Control

* **Auth** – Cognito User Pool; only whitelisted emails may obtain JWT (SRP flow).
* **Authorizer** – Lambda verifies `iss`, `aud`, `exp`; injects `sub` into `requestContext`.
* **GPT Sharing** – *Invite by email* only; disable public discoverability.
* **Secrets** – GPT never receives the Roam token; proxy fetches it from Secrets Manager.

---

## 9  Post-POC Future-Ready Extensions

1. **Vector Index** – nightly export of Roam blocks → Iceberg + OpenSearch for RAG.
2. **LangGraph Agent** – decouple tool-execution logic into a LangGraph graph.
3. **Fine-grained RBAC** – per-page ACL via Roam `[[#access]]` tags enforced by proxy.
4. **Multi-tenant** – graph ID and token per tenant stored in Secrets Manager.

---

## 10  Additional Information

### Problem Statement

Roam knowledge is siloed; manual summarization is slow; interacting via mobile is painful.

### Objective

Provide an AI agent integration layer that ingests, transforms, and acts on Roam data through secure, observable APIs.

|                  |                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------- |
| **Goal**         | secure GPT interaction with shared graph + analytics logging.               |
| **Success KPIs** | • p95 latency < 1 s • ≥ 100 logged interactions in first 30 days • zero credential leaks |

### Stakeholders

| Role               | Name    | Responsibility              |
| ------------------ | ------- | --------------------------- |
| **Developer / PM** | Brock   | Vision, infra, code         |
| **User**           | Partner | Daily use of the Custom GPT |

### Functional Requirements

1. **Read Page** – given title, return JSON of blocks.
2. **Search Blocks** – Datalog query → list of refs.
3. **Append Block** – page ID + markdown text.

### Non-Functional Requirements

* **Security** – see §8.
* **Scalability** – handle 100 RPS bursts.
* **Observability** – 100 % of calls logged; dashboards in CloudWatch.

### Milestones & Timeline

| Date | Milestone        | Owner           |
| ---- | ---------------- | --------------- |
| T+0  | Kick-off         | Brock           |
| T+7  | POC deployed     | Brock           |
| T+9  | Test-suite pass  | Brock           |
| T+14 | Stakeholder demo | Brock & Partner |

### Test Cases

| ID              | Scenario          | Steps                  | Expected Outcome             |
| --------------- | ----------------- | ---------------------- | ---------------------------- |
| **TC-AUTH-001** | Unauthorized user | Call API without JWT   | 401 problem-detail JSON      |
| **TC-PAGE-002** | Fetch page        | Create → Fetch         | 200, correct title           |
| **TC-APP-003**  | Append failure    | Valid page, empty body | 400 “Body must not be empty” |

### Rollback Strategy

CloudFormation/SAM stack rollback; Route 53 cut back to static **503 – Service Unavailable** page.


