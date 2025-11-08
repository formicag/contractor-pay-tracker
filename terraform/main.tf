terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "contractor-pay-terraform-state"
    key    = "terraform.tfstate"
    region = "eu-west-2"
  }
}

provider "aws" {
  region = var.aws_region
}

# DynamoDB Table
resource "aws_dynamodb_table" "contractor_pay" {
  name           = "contractor-pay-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "PK"
  range_key      = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "GSI1PK"
    type = "S"
  }

  attribute {
    name = "GSI1SK"
    type = "S"
  }

  attribute {
    name = "GSI2PK"
    type = "S"
  }

  attribute {
    name = "GSI2SK"
    type = "S"
  }

  attribute {
    name = "GSI3PK"
    type = "S"
  }

  attribute {
    name = "GSI3SK"
    type = "S"
  }

  global_secondary_index {
    name            = "GSI1"
    hash_key        = "GSI1PK"
    range_key       = "GSI1SK"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "GSI2"
    hash_key        = "GSI2PK"
    range_key       = "GSI2SK"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "GSI3"
    hash_key        = "GSI3PK"
    range_key       = "GSI3SK"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  tags = {
    Environment = var.environment
    Application = "contractor-pay-tracker"
  }
}

# S3 Bucket
resource "aws_s3_bucket" "pay_files" {
  bucket = "contractor-pay-files-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Environment = var.environment
    Application = "contractor-pay-tracker"
  }
}

resource "aws_s3_bucket_versioning" "pay_files" {
  bucket = aws_s3_bucket.pay_files.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pay_files" {
  bucket = aws_s3_bucket.pay_files.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "pay_files" {
  bucket = aws_s3_bucket.pay_files.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lambda Layer
data "archive_file" "common_layer" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/layers/common"
  output_path = "${path.module}/.terraform/lambda/common_layer.zip"
}

resource "aws_lambda_layer_version" "common" {
  filename            = data.archive_file.common_layer.output_path
  layer_name          = "contractor-pay-common-${var.environment}"
  compatible_runtimes = ["python3.12"]
  compatible_architectures = ["arm64"]
  source_code_hash    = data.archive_file.common_layer.output_base64sha256
}

# Lambda Functions
data "archive_file" "file_upload_handler" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/functions/file_upload_handler"
  output_path = "${path.module}/.terraform/lambda/file_upload_handler.zip"
}

data "archive_file" "file_processor" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/functions/file_processor"
  output_path = "${path.module}/.terraform/lambda/file_processor.zip"
}

data "archive_file" "validation_engine" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/functions/validation_engine"
  output_path = "${path.module}/.terraform/lambda/validation_engine.zip"
}

data "archive_file" "cleanup_handler" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/functions/cleanup_handler"
  output_path = "${path.module}/.terraform/lambda/cleanup_handler.zip"
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "contractor-pay-lambda-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "contractor-pay-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:*"
        ]
        Resource = [
          aws_dynamodb_table.contractor_pay.arn,
          "${aws_dynamodb_table.contractor_pay.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          aws_s3_bucket.pay_files.arn,
          "${aws_s3_bucket.pay_files.arn}/*"
        ]
      }
    ]
  })
}

# File Upload Handler Lambda
resource "aws_lambda_function" "file_upload_handler" {
  filename         = data.archive_file.file_upload_handler.output_path
  function_name    = "contractor-pay-file-upload-handler-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  runtime         = "python3.12"
  architectures   = ["arm64"]
  timeout         = 30
  memory_size     = 512
  source_code_hash = data.archive_file.file_upload_handler.output_base64sha256

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME     = aws_dynamodb_table.contractor_pay.name
      S3_BUCKET_NAME = aws_s3_bucket.pay_files.bucket
      ENVIRONMENT    = var.environment
      LOG_LEVEL      = var.log_level
    }
  }
}

# File Processor Lambda
resource "aws_lambda_function" "file_processor" {
  filename         = data.archive_file.file_processor.output_path
  function_name    = "contractor-pay-file-processor-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  runtime         = "python3.12"
  architectures   = ["arm64"]
  timeout         = 300
  memory_size     = 1024
  source_code_hash = data.archive_file.file_processor.output_base64sha256

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME     = aws_dynamodb_table.contractor_pay.name
      S3_BUCKET_NAME = aws_s3_bucket.pay_files.bucket
      ENVIRONMENT    = var.environment
      LOG_LEVEL      = var.log_level
    }
  }
}

# Validation Engine Lambda
resource "aws_lambda_function" "validation_engine" {
  filename         = data.archive_file.validation_engine.output_path
  function_name    = "contractor-pay-validation-engine-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  runtime         = "python3.12"
  architectures   = ["arm64"]
  timeout         = 120
  memory_size     = 512
  source_code_hash = data.archive_file.validation_engine.output_base64sha256

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME     = aws_dynamodb_table.contractor_pay.name
      ENVIRONMENT    = var.environment
      LOG_LEVEL      = var.log_level
    }
  }
}

# Cleanup Handler Lambda
resource "aws_lambda_function" "cleanup_handler" {
  filename         = data.archive_file.cleanup_handler.output_path
  function_name    = "contractor-pay-cleanup-handler-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  runtime         = "python3.12"
  architectures   = ["arm64"]
  timeout         = 300
  memory_size     = 256
  source_code_hash = data.archive_file.cleanup_handler.output_base64sha256

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME      = aws_dynamodb_table.contractor_pay.name
      S3_BUCKET_NAME  = aws_s3_bucket.pay_files.bucket
      ENVIRONMENT     = var.environment
      LOG_LEVEL       = var.log_level
      RETENTION_DAYS  = "30"
    }
  }
}

# S3 Trigger Permission
resource "aws_lambda_permission" "s3_trigger" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.file_upload_handler.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.pay_files.arn
}

# S3 Notification
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.pay_files.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.file_upload_handler.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".xlsx"
  }

  depends_on = [aws_lambda_permission.s3_trigger]
}

# Data sources
data "aws_caller_identity" "current" {}
