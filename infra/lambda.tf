resource "aws_lambda_function" "this" {
  function_name = var.lambda_function_name
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  role          = aws_iam_role.lambda_exec.arn
  filename      = "lambda_function_payload.zip"
  memory_size   = 128
  timeout       = 15
  environment {
    variables = {
      FIREHOSE_STREAM_NAME = aws_kinesis_firehose_delivery_stream.analytics.name
    }
  }
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.this.execution_arn}/*/*"
}
