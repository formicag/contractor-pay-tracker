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

# Tagging variables for cost allocation and resource management
variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "contractor-pay-tracker"
}

variable "project_owner" {
  description = "Project owner email or team"
  type        = string
  default     = "engineering-team"
}

variable "cost_center" {
  description = "Cost center for billing"
  type        = string
  default     = "finance-operations"
}

variable "managed_by" {
  description = "Infrastructure management tool"
  type        = string
  default     = "terraform"
}
