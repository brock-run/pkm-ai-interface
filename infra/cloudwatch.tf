resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${var.lambda_function_name}-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alarm if the Lambda function returns any errors"
  dimensions = {
    FunctionName = aws_lambda_function.this.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "api_5xx" {
  alarm_name          = "${var.api_gateway_name}-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "Alarm if the API Gateway returns any 5XX errors"
  dimensions = {
    ApiId = aws_apigatewayv2_api.this.id
    Stage = aws_apigatewayv2_stage.default.name
  }
}

