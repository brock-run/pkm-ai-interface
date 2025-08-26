data "aws_iam_policy_document" "firehose_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }
  }
}

resource "aws_s3_bucket" "analytics" {
  bucket_prefix = "pkm-analytics-"
  force_destroy = true
}

resource "aws_iam_role" "firehose" {
  name               = "firehose-role"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume.json
}

resource "aws_iam_policy" "firehose_s3" {
  name   = "firehose-s3-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:AbortMultipartUpload",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads",
          "s3:ListMultipartUploadParts",
          "s3:PutObject"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.analytics.arn,
          "${aws_s3_bucket.analytics.arn}/*"
        ]
      },
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = aws_lambda_function.analytics_transformer.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "firehose_s3" {
  role       = aws_iam_role.firehose.name
  policy_arn = aws_iam_policy.firehose_s3.arn
}

resource "aws_lambda_function" "analytics_transformer" {
  function_name = "analytics-transformer"
  handler       = "analytics_transformer.lambda_handler"
  runtime       = var.lambda_runtime
  role          = aws_iam_role.lambda_exec.arn
  filename      = "analytics_transformer_payload.zip"
}

resource "aws_lambda_permission" "allow_firehose" {
  statement_id  = "AllowExecutionFromFirehose"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.analytics_transformer.function_name
  principal     = "firehose.amazonaws.com"
  source_arn    = aws_kinesis_firehose_delivery_stream.analytics.arn
}

resource "aws_kinesis_firehose_delivery_stream" "analytics" {
  name        = "analytics-stream"
  destination = "extended_s3"

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.analytics.arn

    processing_configuration {
      enabled = true
      processors {
        type = "Lambda"
        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = aws_lambda_function.analytics_transformer.arn
        }
      }
    }
  }
}

resource "aws_iam_policy" "firehose_write" {
  name   = "firehose-write-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action   = ["firehose:PutRecord"],
      Effect   = "Allow",
      Resource = aws_kinesis_firehose_delivery_stream.analytics.arn
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_firehose" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.firehose_write.arn
}

