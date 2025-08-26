# Secret Retrieval Utility

This project includes a small helper used by AWS Lambda functions to fetch JSON
secrets from AWS Secrets Manager.

```
from src import token_loader

secret = token_loader.load("my/secret", region_name="us-east-1")
token = secret["token"]
```

Secrets should be stored as JSON objects containing a `token` field. The
`ROAM_API_SECRET_NAME` environment variable can be set so the proxy fetches this
secret automatically when `ROAM_API_TOKEN` is not provided.

The function will raise `TokenLoaderError` if the secret cannot be obtained or
the value is not valid JSON.
