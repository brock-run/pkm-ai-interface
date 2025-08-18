resource "aws_cognito_user_pool" "this" {
  name = var.cognito_user_pool_name
}
