#!/bin/bash
# Script to create the Roam API token secret in AWS Secrets Manager
# Usage: ./scripts/create_roam_secret.sh <ROAM_API_TOKEN> [AWS_REGION] [SECRET_NAME]

set -e

# Check if token is provided
if [ -z "$1" ]; then
    echo "Error: Roam API token is required"
    echo ""
    echo "Usage: $0 <ROAM_API_TOKEN> [AWS_REGION] [SECRET_NAME]"
    echo ""
    echo "Example:"
    echo "  $0 'your-roam-api-token-here' us-east-1 roam/prod/apiToken"
    echo ""
    echo "To get your Roam API token:"
    echo "  1. Go to https://roamresearch.com"
    echo "  2. Navigate to your graph settings"
    echo "  3. Generate or copy your API token"
    echo ""
    exit 1
fi

# Configuration
ROAM_API_TOKEN="$1"
AWS_REGION="${2:-us-east-1}"
SECRET_NAME="${3:-roam/prod/apiToken}"

echo "========================================="
echo "Creating Roam API Secret"
echo "========================================="
echo "Region: $AWS_REGION"
echo "Secret Name: $SECRET_NAME"
echo ""

# Create secret JSON
SECRET_JSON=$(cat <<EOF
{
  "token": "$ROAM_API_TOKEN"
}
EOF
)

# Check if secret already exists
echo "Checking if secret exists..."
if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region "$AWS_REGION" 2>/dev/null; then
    echo "Secret already exists. Updating..."
    aws secretsmanager update-secret \
        --secret-id "$SECRET_NAME" \
        --secret-string "$SECRET_JSON" \
        --region "$AWS_REGION"
    echo "✓ Secret updated successfully"
else
    echo "Creating new secret..."
    aws secretsmanager create-secret \
        --name "$SECRET_NAME" \
        --description "Roam Research API token for PKM AI Interface" \
        --secret-string "$SECRET_JSON" \
        --region "$AWS_REGION"
    echo "✓ Secret created successfully"
fi

echo ""
echo "========================================="
echo "SUCCESS!"
echo "========================================="
echo ""
echo "Your secret has been created/updated in AWS Secrets Manager."
echo ""
echo "Use this value for the 'roam_api_secret_name' Terraform variable:"
echo ""
echo "  terraform apply -var=\"roam_api_secret_name=$SECRET_NAME\""
echo ""
echo "Or add to terraform.tfvars:"
echo ""
echo "  roam_api_secret_name = \"$SECRET_NAME\""
echo ""
echo "Note: Make sure your Lambda IAM role has permission to access this secret."
echo "The Terraform configuration has been updated to grant this permission."
echo ""
