# Secret Retrieval Utility

This project includes a small helper used by AWS Lambda functions to fetch JSON
secrets from AWS Secrets Manager.

```
from src import token_loader

secret = token_loader.load("my/secret", region_name="us-east-1")
```

The function will raise `TokenLoaderError` if the secret cannot be obtained or
the value is not valid JSON.
