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
  name         = "contractor-pay-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

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

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-${var.environment}"
    Service     = "dynamodb"
    Description = "Primary database for contractor pay tracking"
  })
}

# S3 Bucket
resource "aws_s3_bucket" "pay_files" {
  bucket = "contractor-pay-files-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-files-${var.environment}"
    Service     = "s3"
    Description = "Storage for contractor pay Excel files and reports"
  })
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
  filename                 = data.archive_file.common_layer.output_path
  layer_name               = "contractor-pay-common-${var.environment}"
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["arm64"]
  source_code_hash         = data.archive_file.common_layer.output_base64sha256
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

data "archive_file" "report_generator" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/functions/report_generator"
  output_path = "${path.module}/.terraform/lambda/report_generator.zip"
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

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-lambda-${var.environment}"
    Service     = "iam"
    Description = "Execution role for Lambda functions"
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
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v2:0",
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-embed-text-v1"
        ]
      }
    ]
  })
}

# File Upload Handler Lambda
resource "aws_lambda_function" "file_upload_handler" {
  filename         = data.archive_file.file_upload_handler.output_path
  function_name    = "contractor-pay-file-upload-handler-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["arm64"]
  timeout          = 30
  memory_size      = 512
  source_code_hash = data.archive_file.file_upload_handler.output_base64sha256

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME        = aws_dynamodb_table.contractor_pay.name
      S3_BUCKET_NAME    = aws_s3_bucket.pay_files.bucket
      STEP_FUNCTION_ARN = "arn:aws:states:${var.aws_region}:${data.aws_caller_identity.current.account_id}:stateMachine:contractor-pay-workflow-${var.environment}"
      ENVIRONMENT       = var.environment
      LOG_LEVEL         = var.log_level
    }
  }

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-file-upload-handler-${var.environment}"
    Service     = "lambda"
    Function    = "file-upload-handler"
    Description = "Handles S3 file upload events and initiates processing"
  })
}

# File Processor Lambda
resource "aws_lambda_function" "file_processor" {
  filename         = data.archive_file.file_processor.output_path
  function_name    = "contractor-pay-file-processor-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["arm64"]
  timeout          = 300
  memory_size      = 1024
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

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-file-processor-${var.environment}"
    Service     = "lambda"
    Function    = "file-processor"
    Description = "Processes Excel files and extracts contractor pay data"
  })
}

# Validation Engine Lambda
resource "aws_lambda_function" "validation_engine" {
  filename         = data.archive_file.validation_engine.output_path
  function_name    = "contractor-pay-validation-engine-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["arm64"]
  timeout          = 120
  memory_size      = 512
  source_code_hash = data.archive_file.validation_engine.output_base64sha256

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.contractor_pay.name
      ENVIRONMENT = var.environment
      LOG_LEVEL   = var.log_level
    }
  }

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-validation-engine-${var.environment}"
    Service     = "lambda"
    Function    = "validation-engine"
    Description = "Validates contractor pay records against business rules"
  })
}

# Cleanup Handler Lambda
resource "aws_lambda_function" "cleanup_handler" {
  filename         = data.archive_file.cleanup_handler.output_path
  function_name    = "contractor-pay-cleanup-handler-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["arm64"]
  timeout          = 300
  memory_size      = 256
  source_code_hash = data.archive_file.cleanup_handler.output_base64sha256

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME     = aws_dynamodb_table.contractor_pay.name
      S3_BUCKET_NAME = aws_s3_bucket.pay_files.bucket
      ENVIRONMENT    = var.environment
      LOG_LEVEL      = var.log_level
      RETENTION_DAYS = "30"
    }
  }

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-cleanup-handler-${var.environment}"
    Service     = "lambda"
    Function    = "cleanup-handler"
    Description = "Manages data retention and cleanup of old records"
  })
}

# Report Generator Lambda
resource "aws_lambda_function" "report_generator" {
  filename         = data.archive_file.report_generator.output_path
  function_name    = "contractor-pay-report-generator-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.12"
  architectures    = ["arm64"]
  timeout          = 120
  memory_size      = 512
  source_code_hash = data.archive_file.report_generator.output_base64sha256

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME     = aws_dynamodb_table.contractor_pay.name
      S3_BUCKET_NAME = aws_s3_bucket.pay_files.bucket
      ENVIRONMENT    = var.environment
      LOG_LEVEL      = var.log_level
    }
  }

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-report-generator-${var.environment}"
    Service     = "lambda"
    Function    = "report-generator"
    Description = "Generates contractor pay reports and summaries"
  })
}

# S3 Trigger Permission
resource "aws_lambda_permission" "s3_trigger" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.file_upload_handler.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.pay_files.arn
}

# S3 EventBridge Notification (replaces Lambda notification for SQS architecture)
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket      = aws_s3_bucket.pay_files.id
  eventbridge = true
}

# Data sources
data "aws_caller_identity" "current" {}

# ===========================
# Step Functions Resources
# ===========================

# IAM Role for Step Functions
resource "aws_iam_role" "step_functions_role" {
  name = "contractor-pay-step-functions-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-step-functions-${var.environment}"
    Service     = "iam"
    Description = "Execution role for Step Functions workflow"
  })
}

# IAM Policy for Step Functions to invoke Lambda
resource "aws_iam_role_policy" "step_functions_policy" {
  name = "contractor-pay-step-functions-policy"
  role = aws_iam_role.step_functions_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:contractor-pay-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogDelivery",
          "logs:GetLogDelivery",
          "logs:UpdateLogDelivery",
          "logs:DeleteLogDelivery",
          "logs:ListLogDeliveries",
          "logs:PutResourcePolicy",
          "logs:DescribeResourcePolicies",
          "logs:DescribeLogGroups"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch Log Group for Step Functions
resource "aws_cloudwatch_log_group" "step_functions" {
  name              = "/aws/vendedlogs/states/contractor-pay-workflow-${var.environment}"
  retention_in_days = 30

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-workflow-logs-${var.environment}"
    Service     = "cloudwatch"
    Description = "Step Functions workflow execution logs"
  })
}

# Step Functions State Machine
resource "aws_sfn_state_machine" "contractor_pay_workflow" {
  name     = "contractor-pay-workflow-${var.environment}"
  role_arn = aws_iam_role.step_functions_role.arn

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.step_functions.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  definition = jsonencode({
    Comment = "Contractor Pay File Processing Workflow"
    StartAt = "ExtractMetadata"
    States = {
      # Step 2: Extract Metadata
      ExtractMetadata = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"   = "extract_metadata"
          "fileId.$" = "$.fileId"
          "bucket.$" = "$.s3_bucket"
          "key.$"    = "$.key"
        }
        ResultPath = "$.metadata"
        Next       = "MatchPeriod"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "ProcessingFailedHandler"
          }
        ]
        TimeoutSeconds = 60
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException", "Lambda.TooManyRequestsException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
      }

      # Step 3: Match Period
      MatchPeriod = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"     = "match_period"
          "fileId.$"   = "$.fileId"
          "metadata.$" = "$.metadata"
        }
        ResultPath = "$.period"
        Next       = "CheckDuplicates"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "ProcessingFailedHandler"
          }
        ]
        TimeoutSeconds = 30
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
      }

      # Step 4: Check Duplicates
      CheckDuplicates = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"   = "check_duplicates"
          "fileId.$" = "$.fileId"
          "period.$" = "$.period"
        }
        ResultPath = "$.duplicates"
        Next       = "DuplicatesFound"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "ProcessingFailedHandler"
          }
        ]
        TimeoutSeconds = 30
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
      }

      # Step 5: Choice - Are there duplicates?
      DuplicatesFound = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.duplicates.hasDuplicates"
            BooleanEquals = true
            Next          = "SupersedeExisting"
          }
        ]
        Default = "ParseRecords"
      }

      # Step 5: Supersede Existing (Conditional)
      SupersedeExisting = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"             = "supersede_existing"
          "fileId.$"           = "$.fileId"
          "existing_file_id.$" = "$.duplicates.existing_file_id"
        }
        ResultPath = "$.superseded"
        Next       = "ParseRecords"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "ProcessingFailedHandler"
          }
        ]
        TimeoutSeconds = 60
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
      }

      # Step 6: Parse Records
      ParseRecords = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"     = "parse_records"
          "fileId.$"   = "$.fileId"
          "bucket.$"   = "$.s3_bucket"
          "key.$"      = "$.key"
          "metadata.$" = "$.metadata"
          "period.$"   = "$.period"
        }
        ResultPath = "$.parsedRecords"
        Next       = "ValidateRecords"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "ProcessingFailedHandler"
          }
        ]
        TimeoutSeconds = 300
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 2
            MaxAttempts     = 2
            BackoffRate     = 2.0
          }
        ]
      }

      # Step 7: Validate Records
      ValidateRecords = {
        Type     = "Task"
        Resource = aws_lambda_function.validation_engine.arn
        Parameters = {
          "file_id.$"     = "$.fileId"
          "umbrella_id.$" = "$.period.umbrella_id"
          "period_id.$"   = "$.period.period_id"
          "records.$"     = "$.parsedRecords.records"
        }
        ResultSelector = {
          "hasCriticalErrors.$" = "$.has_critical_errors"
          "hasWarnings.$"       = "$.has_warnings"
          "validatedRecords.$"  = "$.validated_records"
          "errors.$"            = "$.errors"
          "warnings.$"          = "$.warnings"
        }
        ResultPath = "$.validation"
        Next       = "HasCriticalErrors"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "ProcessingFailedHandler"
          }
        ]
        TimeoutSeconds = 120
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2.0
          }
        ]
      }

      # Step 8: Choice - Critical Errors?
      HasCriticalErrors = {
        Type = "Choice"
        Choices = [
          {
            Variable      = "$.validation.hasCriticalErrors"
            BooleanEquals = true
            Next          = "ValidationErrorHandler"
          }
        ]
        Default = "ImportRecords"
      }

      # Step 8: Import Records (Conditional)
      ImportRecords = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"       = "import_records"
          "fileId.$"     = "$.fileId"
          "records.$"    = "$.parsedRecords.records"
          "validation.$" = "$.validation"
        }
        ResultPath = "$.import"
        Next       = "MarkComplete"
        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            ResultPath  = "$.error"
            Next        = "ProcessingFailedHandler"
          }
        ]
        TimeoutSeconds = 300
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 2
            MaxAttempts     = 2
            BackoffRate     = 2.0
          }
        ]
      }

      # Step 9a: Mark Complete - Mark file as successfully processed
      MarkComplete = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"   = "mark_complete"
          "fileId.$" = "$.fileId"
          "import.$" = "$.import"
        }
        ResultPath     = "$.completed"
        Next           = "Success"
        TimeoutSeconds = 30
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 1
            MaxAttempts     = 2
            BackoffRate     = 1.5
          }
        ]
      }

      # Validation Error Handler - Mark file with validation errors, no import
      ValidationErrorHandler = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"              = "mark_error"
          "fileId.$"            = "$.fileId"
          "validation_errors.$" = "$.validation.errors"
        }
        ResultPath     = "$.errorMarked"
        Next           = "Failed"
        TimeoutSeconds = 30
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 1
            MaxAttempts     = 2
            BackoffRate     = 1.5
          }
        ]
      }

      # Processing Failed Handler - Mark file as failed due to system error
      ProcessingFailedHandler = {
        Type     = "Task"
        Resource = aws_lambda_function.file_processor.arn
        Parameters = {
          "action"   = "mark_failed"
          "fileId.$" = "$.fileId"
          "error.$"  = "$.error"
        }
        ResultPath     = "$.errorMarked"
        Next           = "Failed"
        TimeoutSeconds = 30
        Retry = [
          {
            ErrorEquals     = ["States.TaskFailed", "Lambda.ServiceException"]
            IntervalSeconds = 1
            MaxAttempts     = 2
            BackoffRate     = 1.5
          }
        ]
      }

      # Success State
      Success = {
        Type = "Succeed"
      }

      # Failed State
      Failed = {
        Type  = "Fail"
        Error = "WorkflowFailed"
        Cause = "The file processing workflow encountered an error"
      }
    }
  })

  tags = merge(local.common_tags, {
    Name        = "contractor-pay-workflow-${var.environment}"
    Service     = "step-functions"
    Description = "Orchestrates contractor pay file processing workflow"
  })

  depends_on = [
    aws_iam_role_policy.step_functions_policy,
    aws_cloudwatch_log_group.step_functions
  ]
}

# Lambda permission for Step Functions to invoke file_processor
resource "aws_lambda_permission" "step_functions_file_processor" {
  statement_id  = "AllowStepFunctionsInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.file_processor.function_name
  principal     = "states.amazonaws.com"
  source_arn    = aws_sfn_state_machine.contractor_pay_workflow.arn
}

# Lambda permission for Step Functions to invoke validation_engine
resource "aws_lambda_permission" "step_functions_validation_engine" {
  statement_id  = "AllowStepFunctionsInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.validation_engine.function_name
  principal     = "states.amazonaws.com"
  source_arn    = aws_sfn_state_machine.contractor_pay_workflow.arn
}

# Lambda policy to allow starting Step Functions executions
resource "aws_iam_role_policy" "lambda_step_functions_policy" {
  name = "contractor-pay-lambda-step-functions-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "states:StartExecution",
          "states:DescribeExecution"
        ]
        Resource = [
          aws_sfn_state_machine.contractor_pay_workflow.arn,
          "${aws_sfn_state_machine.contractor_pay_workflow.arn}:*"
        ]
      }
    ]
  })
}
