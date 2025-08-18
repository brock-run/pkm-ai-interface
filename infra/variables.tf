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

variable "lambda_handler" {
  description = "Lambda handler"
  type        = string
  default     = "index.handler"
}

variable "lambda_runtime" {
  description = "Runtime for the Lambda function"
  type        = string
  default     = "python3.11"
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
