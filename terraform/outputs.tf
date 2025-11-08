output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.contractor_pay.name
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.pay_files.bucket
}

output "file_upload_handler_arn" {
  description = "File upload handler Lambda ARN"
  value       = aws_lambda_function.file_upload_handler.arn
}

output "file_processor_arn" {
  description = "File processor Lambda ARN"
  value       = aws_lambda_function.file_processor.arn
}

output "validation_engine_arn" {
  description = "Validation engine Lambda ARN"
  value       = aws_lambda_function.validation_engine.arn
}

output "cleanup_handler_arn" {
  description = "Cleanup handler Lambda ARN"
  value       = aws_lambda_function.cleanup_handler.arn
}
