#!/bin/bash
# Script to build and push the Lambda container image to ECR
# Usage: ./scripts/build_and_push_ecr.sh [AWS_REGION] [ECR_REPO_NAME]

set -e

# Configuration
AWS_REGION="${1:-us-east-1}"
ECR_REPO_NAME="${2:-roam-mcp-proxy}"

echo "========================================="
echo "Building and Pushing Lambda Container"
echo "========================================="
echo "Region: $AWS_REGION"
echo "Repository: $ECR_REPO_NAME"
echo ""

# Get AWS account ID
echo "Getting AWS account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account ID: $AWS_ACCOUNT_ID"
echo ""

# ECR repository URI
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Step 1: Create ECR repository if it doesn't exist
echo "Step 1: Creating ECR repository (if not exists)..."
aws ecr describe-repositories --repository-names "$ECR_REPO_NAME" --region "$AWS_REGION" 2>/dev/null || \
    aws ecr create-repository \
        --repository-name "$ECR_REPO_NAME" \
        --region "$AWS_REGION" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256

echo "✓ Repository ready"
echo ""

# Step 2: Log in to ECR
echo "Step 2: Logging in to ECR..."
aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin "$ECR_URI"
echo "✓ Logged in successfully"
echo ""

# Step 3: Build the Docker image
echo "Step 3: Building Docker image..."
cd "$(dirname "$0")/.."
docker build \
    --platform linux/arm64 \
    -t "$ECR_REPO_NAME:latest" \
    -f src/Dockerfile \
    src/
echo "✓ Image built successfully"
echo ""

# Step 4: Tag the image
echo "Step 4: Tagging image..."
docker tag "$ECR_REPO_NAME:latest" "$ECR_URI:latest"
echo "✓ Image tagged as: $ECR_URI:latest"
echo ""

# Step 5: Push to ECR
echo "Step 5: Pushing image to ECR..."
docker push "$ECR_URI:latest"
echo "✓ Image pushed successfully"
echo ""

# Display the image URI
echo "========================================="
echo "SUCCESS!"
echo "========================================="
echo ""
echo "Your Lambda image URI is:"
echo ""
echo "  $ECR_URI:latest"
echo ""
echo "Use this value for the 'lambda_image_uri' Terraform variable:"
echo ""
echo "  terraform apply -var=\"lambda_image_uri=$ECR_URI:latest\""
echo ""
echo "Or add to terraform.tfvars:"
echo ""
echo "  lambda_image_uri = \"$ECR_URI:latest\""
echo ""
