# Infrastructure Terraform Skeleton

## Approach
- Define IAM role and policy allowing Lambda to assume role, write CloudWatch logs, and read Secrets Manager.
- Configure Lambda function with 128 MB memory and 15‑second timeout.
- Expose the Lambda through API Gateway using a proxy resource and AWS_PROXY integration.
- Create a Kinesis Firehose delivery stream that invokes the `analytics_transformer`
  Lambda to enrich events before writing to S3.
- Provide a minimal Cognito user pool for authentication scaffolding.
- Supply variables and outputs to parameterize core identifiers such as
  `ROAM_API_SECRET_NAME` and `FIREHOSE_STREAM_NAME`.

## Verified
- IAM policy includes `secretsmanager:GetSecretValue` and CloudWatch Logs permissions.
- Lambda function configured with 128 MB memory and 15‑second timeout.
- `terraform init -backend=false` attempted but failed to download provider plugins due to a forbidden request to the Terraform Registry.
- `terraform validate` attempted but failed because the AWS provider plugin was not initialized.

## Remaining Work
- Obtain AWS provider plugins or configure Terraform to run in an offline environment so `terraform init` and `terraform validate` succeed.
- Flesh out analytics Firehose configuration and other infrastructure modules as needed.
- Add automated testing or CI to exercise Terraform configuration in future.
