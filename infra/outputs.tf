output "lambda_function_arn" {
  value = aws_lambda_function.this.arn
}

output "api_gateway_id" {
  value = aws_api_gateway_rest_api.this.id
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.this.id
}

output "iam_role_arn" {
  value = aws_iam_role.lambda_exec.arn
}
