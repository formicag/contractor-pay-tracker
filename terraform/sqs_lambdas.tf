# =============================================================================
# SQS-Triggered Lambda Functions (NO STEP FUNCTIONS)
# =============================================================================

# -----------------------------------------------------------------------------
# Lambda 1: Extract Metadata
# Triggered by: upload-queue
# Sends to: validation-queue
# -----------------------------------------------------------------------------
data "archive_file" "extract_metadata" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/functions/extract_metadata"
  output_path = "${path.module}/.terraform/extract_metadata.zip"
}

resource "aws_lambda_function" "extract_metadata" {
  filename         = data.archive_file.extract_metadata.output_path
  function_name    = "contractor-pay-extract-metadata-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  source_code_hash = data.archive_file.extract_metadata.output_base64sha256
  runtime         = "python3.12"
  timeout         = 300
  memory_size     = 512

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME            = aws_dynamodb_table.contractor_pay.name
      VALIDATION_QUEUE_URL  = aws_sqs_queue.validation_queue.url
      ENVIRONMENT           = var.environment
    }
  }

  tags = {
    Environment = var.environment
    Project     = "contractor-pay-tracker"
    ManagedBy   = "terraform"
    Name        = "contractor-pay-extract-metadata-${var.environment}"
    Function    = "extract-metadata"
    Description = "Extract metadata from uploaded Excel files"
  }
}

# SQS trigger for extract-metadata Lambda
resource "aws_lambda_event_source_mapping" "extract_metadata_trigger" {
  event_source_arn = aws_sqs_queue.upload_queue.arn
  function_name    = aws_lambda_function.extract_metadata.arn
  batch_size       = 1  # Process 1 file at a time
  enabled          = true

  depends_on = [aws_iam_role_policy.lambda_sqs_policy]
}

# -----------------------------------------------------------------------------
# Lambda 2: Validate Data
# Triggered by: validation-queue
# Sends to: import-queue
# -----------------------------------------------------------------------------
data "archive_file" "validate_data" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/functions/validate_data"
  output_path = "${path.module}/.terraform/validate_data.zip"
}

resource "aws_lambda_function" "validate_data" {
  filename         = data.archive_file.validate_data.output_path
  function_name    = "contractor-pay-validate-data-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  source_code_hash = data.archive_file.validate_data.output_base64sha256
  runtime         = "python3.12"
  timeout         = 600  # Validation can take time
  memory_size     = 1024

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME       = aws_dynamodb_table.contractor_pay.name
      IMPORT_QUEUE_URL = aws_sqs_queue.import_queue.url
      ENVIRONMENT      = var.environment
    }
  }

  tags = {
    Environment = var.environment
    Project     = "contractor-pay-tracker"
    ManagedBy   = "terraform"
    Name        = "contractor-pay-validate-data-${var.environment}"
    Function    = "validate-data"
    Description = "Enterprise-grade data validation"
  }
}

resource "aws_lambda_event_source_mapping" "validate_data_trigger" {
  event_source_arn = aws_sqs_queue.validation_queue.arn
  function_name    = aws_lambda_function.validate_data.arn
  batch_size       = 1
  enabled          = true

  depends_on = [aws_iam_role_policy.lambda_sqs_policy]
}

# -----------------------------------------------------------------------------
# Lambda 3: Import Records
# Triggered by: import-queue
# Final stage: Writes to DynamoDB
# -----------------------------------------------------------------------------
data "archive_file" "import_records" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/functions/import_records"
  output_path = "${path.module}/.terraform/import_records.zip"
}

resource "aws_lambda_function" "import_records" {
  filename         = data.archive_file.import_records.output_path
  function_name    = "contractor-pay-import-records-${var.environment}"
  role            = aws_iam_role.lambda_role.arn
  handler         = "app.lambda_handler"
  source_code_hash = data.archive_file.import_records.output_base64sha256
  runtime         = "python3.12"
  timeout         = 600  # Batch imports can take time
  memory_size     = 1024

  layers = [aws_lambda_layer_version.common.arn]

  environment {
    variables = {
      TABLE_NAME  = aws_dynamodb_table.contractor_pay.name
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    Environment = var.environment
    Project     = "contractor-pay-tracker"
    ManagedBy   = "terraform"
    Name        = "contractor-pay-import-records-${var.environment}"
    Function    = "import-records"
    Description = "Import validated records to DynamoDB"
  }
}

resource "aws_lambda_event_source_mapping" "import_records_trigger" {
  event_source_arn = aws_sqs_queue.import_queue.arn
  function_name    = aws_lambda_function.import_records.arn
  batch_size       = 1
  enabled          = true

  depends_on = [aws_iam_role_policy.lambda_sqs_policy]
}

# -----------------------------------------------------------------------------
# IAM Permissions for SQS
# -----------------------------------------------------------------------------

# Allow Lambdas to read from their respective SQS queues
resource "aws_iam_role_policy" "lambda_sqs_policy" {
  name = "lambda-sqs-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.upload_queue.arn,
          aws_sqs_queue.validation_queue.arn,
          aws_sqs_queue.import_queue.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = [
          aws_sqs_queue.validation_queue.arn,
          aws_sqs_queue.import_queue.arn
        ]
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------
output "extract_metadata_arn" {
  value       = aws_lambda_function.extract_metadata.arn
  description = "ARN of extract-metadata Lambda"
}

output "validate_data_arn" {
  value       = aws_lambda_function.validate_data.arn
  description = "ARN of validate-data Lambda"
}

output "import_records_arn" {
  value       = aws_lambda_function.import_records.arn
  description = "ARN of import-records Lambda"
}
