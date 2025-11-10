# Common tags to be applied to all resources
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.project_owner
    Purpose     = "contractor-payroll-processing"
    ManagedBy   = var.managed_by
    CostCenter  = var.cost_center
    CreatedBy   = "terraform"
  }
}
