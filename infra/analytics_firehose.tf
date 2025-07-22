# Terraform snippet for analytics Firehose
resource "aws_kinesis_firehose_delivery_stream" "analytics" {
  name        = "analytics-stream"
  destination = "s3"

  s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.analytics.arn
  }
}

resource "aws_iam_role" "firehose" {
  name = "firehose-role"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume.json
}

resource "aws_iam_policy" "firehose_write" {
  name   = "firehose-write-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action   = ["firehose:PutRecord"]
      Effect   = "Allow"
      Resource = aws_kinesis_firehose_delivery_stream.analytics.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_firehose" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.firehose_write.arn
}
