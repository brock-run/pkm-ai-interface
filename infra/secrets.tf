# Roam API Secret Management
# This references an existing secret - create it first using the setup script
#
# To create the secret manually:
# aws secretsmanager create-secret \
#   --name roam/prod/apiToken \
#   --secret-string '{"token":"YOUR_ROAM_API_TOKEN_HERE"}' \
#   --region us-east-1

data "aws_secretsmanager_secret" "roam_api_token" {
  count = var.roam_api_secret_name != "" ? 1 : 0
  name  = var.roam_api_secret_name
}
