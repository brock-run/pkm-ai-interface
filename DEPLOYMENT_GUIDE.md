# Deployment Guide - First Working Version

This guide will help you deploy the Roam MCP Proxy to AWS and get a working prototype.

## Prerequisites

- AWS CLI configured with appropriate credentials
- Docker installed and running
- Terraform installed (v1.0+)
- Your Roam Research API token
- AWS account with permissions for:
  - Lambda
  - API Gateway
  - Cognito
  - S3
  - Kinesis Firehose
  - IAM
  - CloudWatch
  - Secrets Manager
  - ECR

## Step-by-Step Deployment

### Step 1: Create Roam API Secret

First, store your Roam API token in AWS Secrets Manager:

```bash
./scripts/create_roam_secret.sh "YOUR_ROAM_API_TOKEN_HERE" us-east-1 roam/prod/apiToken
```

This creates a secret named `roam/prod/apiToken` containing your token.

### Step 2: Build and Push Container Image

Build the Lambda container image and push it to ECR:

```bash
./scripts/build_and_push_ecr.sh us-east-1 roam-mcp-proxy
```

This script will:
- Create an ECR repository (if needed)
- Build the Docker image for ARM64 Lambda
- Tag and push the image to ECR
- Display the image URI you'll need for Terraform

**Save the image URI** displayed at the end - you'll need it in the next step.

### Step 3: Configure Terraform Variables

Create a `terraform.tfvars` file in the `infra/` directory:

```bash
cat > infra/terraform.tfvars <<EOF
# Required: ECR image URI from Step 2
lambda_image_uri = "123456789012.dkr.ecr.us-east-1.amazonaws.com/roam-mcp-proxy:latest"

# Required: Secret name from Step 1
roam_api_secret_name = "roam/prod/apiToken"

# Optional: Customize these if desired
aws_region              = "us-east-1"
lambda_function_name    = "pkm-function"
api_gateway_name        = "pkm-api"
cognito_user_pool_name  = "pkm-user-pool"
EOF
```

**Replace the `lambda_image_uri` value** with the actual URI from Step 2.

### Step 4: Initialize and Deploy Terraform

```bash
cd infra

# Initialize Terraform (downloads providers)
terraform init

# Format code
terraform fmt

# Validate configuration
terraform validate

# Preview changes
terraform plan

# Deploy (type 'yes' when prompted)
terraform apply
```

**Save the outputs** displayed after `terraform apply` - they contain your API Gateway URL.

### Step 5: Create Cognito Users

Create users who can access your API:

```bash
# Get the User Pool ID from Terraform outputs
USER_POOL_ID=$(cd infra && terraform output -raw cognito_user_pool_id)

# Create a user (replace with actual email)
aws cognito-idp admin-create-user \
  --user-pool-id "$USER_POOL_ID" \
  --username "your-email@example.com" \
  --user-attributes Name=email,Value="your-email@example.com" \
  --message-action SUPPRESS

# Set a permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id "$USER_POOL_ID" \
  --username "your-email@example.com" \
  --password "YourSecurePassword123!" \
  --permanent

# Repeat for the second whitelisted user
```

### Step 6: Get Authentication Token

To call your API, you need a JWT token from Cognito:

```bash
# Get the User Pool Client ID
CLIENT_ID=$(cd infra && terraform output -raw cognito_client_id)

# Authenticate and get token
aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME="your-email@example.com",PASSWORD="YourSecurePassword123!" \
  --query 'AuthenticationResult.IdToken' \
  --output text
```

**Save this token** - you'll use it as a Bearer token in API requests.

### Step 7: Test the Deployment

Get your API Gateway URL:

```bash
cd infra
terraform output api_gateway_url
```

Test the `/analytics/log` endpoint:

```bash
API_URL=$(cd infra && terraform output -raw api_gateway_url)
JWT_TOKEN="<your-token-from-step-6>"

curl -X POST "$API_URL/analytics/log" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "test",
    "message": "Hello from deployment test"
  }'
```

Test a Roam proxy endpoint (e.g., fetch a page):

```bash
curl -X POST "$API_URL/roam_fetch_page" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "page_title": "Your Page Title"
  }'
```

### Step 8: Run Smoke Tests

Run the automated smoke tests against your deployment:

```bash
# Set environment variables
export ROAM_API_BASE="$API_URL"
export COGNITO_USER_POOL_ID="$USER_POOL_ID"
export COGNITO_CLIENT_ID="$CLIENT_ID"
export TEST_USERNAME="your-email@example.com"
export TEST_PASSWORD="YourSecurePassword123!"

# Run smoke tests
pytest tests/smoke/ -m prod -v
```

### Step 9: Configure Custom GPT

Now configure your Custom GPT in OpenAI:

1. Go to ChatGPT → Create a GPT
2. Configure authentication:
   - Type: OAuth
   - Authorization URL: `https://cognito-idp.us-east-1.amazonaws.com/<user-pool-id>/oauth2/authorize`
   - Token URL: `https://cognito-idp.us-east-1.amazonaws.com/<user-pool-id>/oauth2/token`
   - Scope: `openid email`
3. Import actions from OpenAPI schema:
   - Generate schema: `./scripts/generate_openapi.sh`
   - Upload the generated `docs/openapi_trim.json`
4. Set your API base URL to the API Gateway URL

## What Was Fixed

The following critical blockers were resolved:

### 1. ✅ Missing Terraform Variable
- **File**: `infra/variables.tf`
- **Fix**: Added `lambda_runtime` variable with default value "python3.12"

### 2. ✅ Analytics Transformer Deployment
- **File**: `infra/analytics_firehose.tf`
- **Fix**: Added Terraform `archive_file` data source to automatically package `analytics_transformer.py`
- **Benefit**: No manual zip file creation needed

### 3. ✅ Custom Domain Requirement
- **File**: `infra/apigw.tf`
- **Fix**: Set `disable_execute_api_endpoint = false` to use default API Gateway URL
- **Fix**: Commented out custom domain resources (domain name, API mapping, Route53 record)
- **Benefit**: Can deploy without ACM certificate or Route53 zone

### 4. ✅ IAM Policy Wildcards
- **File**: `infra/iam.tf`
- **Fix**: Scoped CloudWatch Logs to specific Lambda log groups
- **Fix**: Scoped Secrets Manager to specific secret ARN
- **Fix**: Added data sources for AWS account ID and region
- **Benefit**: Follows least privilege principle

### 5. ✅ Secret Management
- **File**: `infra/secrets.tf` (new)
- **Fix**: Created data source to reference existing secret
- **Script**: `scripts/create_roam_secret.sh` for easy secret creation
- **Benefit**: Proper secret lifecycle management

### 6. ✅ ECR Image Build Process
- **Script**: `scripts/build_and_push_ecr.sh`
- **Fix**: Automated ECR repository creation, image build, and push
- **Benefit**: One-command deployment of Lambda container

## Verification

After deployment, verify these components:

- [ ] Lambda function exists and is running
- [ ] API Gateway endpoint is accessible
- [ ] Cognito user pool has users
- [ ] Can authenticate and get JWT token
- [ ] Analytics events are logged to S3
- [ ] CloudWatch logs show Lambda invocations
- [ ] Secret is accessible by Lambda

## Troubleshooting

### "Secret not found" error
- Ensure you ran Step 1 and created the secret
- Verify the secret name matches `roam_api_secret_name` in terraform.tfvars

### "Lambda function failed to create"
- Check that `lambda_image_uri` in terraform.tfvars matches the ECR URI
- Verify the image was pushed successfully in Step 2

### "Unauthorized" when calling API
- Ensure you're using a valid JWT token from Step 6
- Verify the user exists in Cognito
- Check that the token hasn't expired (tokens expire after 1 hour)

### Terraform validation fails
- Run `terraform fmt` to format files
- Run `terraform validate` to see specific errors
- Check that all required variables are set

### Docker build fails
- Ensure Docker is running
- Check that you have ARM64 emulation enabled (for Mac M1/M2)
- Try `docker buildx ls` to verify builder support

## Next Steps

Once you have a working deployment:

1. **Test thoroughly** - Try all Roam API operations
2. **Monitor costs** - Check AWS billing for Lambda, API Gateway, Firehose usage
3. **Set up alerts** - Configure SNS topics for CloudWatch alarms
4. **Document issues** - Note any bugs or missing features
5. **Plan improvements** - Review the PRD for Phase 2 features

## Optional: Enable Custom Domain

To use a custom domain instead of the default API Gateway URL:

1. **Request ACM certificate** for your domain
2. **Create Route53 hosted zone** (if you don't have one)
3. **Update variables** in terraform.tfvars:
   ```hcl
   custom_domain_name  = "api.yourdomain.com"
   acm_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/abc123..."
   route53_zone_id     = "Z1234567890ABC"
   ```
4. **Uncomment custom domain resources** in `infra/apigw.tf`
5. **Set** `disable_execute_api_endpoint = true` in `infra/apigw.tf`
6. **Re-run** `terraform apply`

## Cost Estimate

Expected monthly costs for light usage (< 1000 requests/day):

- Lambda: ~$5-10
- API Gateway: ~$3-5
- Cognito: Free tier (< 50,000 MAU)
- S3: < $1
- Firehose: ~$1-2
- CloudWatch: ~$1-2

**Total**: ~$10-20/month for development/testing

## Support

If you encounter issues:

1. Check CloudWatch Logs for error messages
2. Review Terraform state: `terraform show`
3. Validate IAM permissions
4. Consult the main README.md
5. Review `.taskmaster/prd.md` for architecture details
