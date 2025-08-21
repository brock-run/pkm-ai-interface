terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "pkm-function"
}

variable "api_gateway_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = "pkm-api"
}

variable "cognito_user_pool_name" {
  description = "Name of the Cognito user pool"
  type        = string
  default     = "pkm-user-pool"
}

variable "lambda_image_uri" {
  description = "ECR image URI for the Lambda function"
  type        = string
  default     = ""
}

variable "roam_api_secret_name" {
  description = "Secrets Manager secret name for the ROAM API token"
  type        = string
  default     = ""
}

variable "custom_domain_name" {
  description = "Custom domain name for the API Gateway"
  type        = string
  default     = "api.example.com"
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for the custom domain"
  type        = string
  default     = "arn:aws:acm:us-east-1:123456789012:certificate/example"
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for the custom domain"
  type        = string
  default     = "Z1234567890ABC"
}
