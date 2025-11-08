variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "log_level" {
  description = "Lambda function logging level"
  type        = string
  default     = "DEBUG"
}
