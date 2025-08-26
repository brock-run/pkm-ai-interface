output "lambda_function_arn" {
  value = aws_lambda_function.this.arn
}

output "api_gateway_id" {
  value = aws_apigatewayv2_api.this.id
}

output "cognito_user_pool_id" {
  value = aws_cognito_user_pool.this.id
}

output "cognito_user_pool_client_id" {
  value = aws_cognito_user_pool_client.this.id
}

output "api_domain_name" {
  value = aws_apigatewayv2_domain_name.this.domain_name
}

output "iam_role_arn" {
  value = aws_iam_role.lambda_exec.arn
}
