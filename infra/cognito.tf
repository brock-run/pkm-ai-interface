resource "aws_cognito_user_pool" "this" {
  name = var.cognito_user_pool_name
}

resource "aws_cognito_user_pool_client" "this" {
  name         = "${var.cognito_user_pool_name}-client"
  user_pool_id = aws_cognito_user_pool.this.id
}
