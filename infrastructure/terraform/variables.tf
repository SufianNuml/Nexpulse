variable "location" {
  description = "Azure region for Nexpulse resources"
  type        = string
  default     = "uaenorth"
}

variable "project_name" {
  description = "Project name used for Azure resource naming"
  type        = string
  default     = "nexpulse"
}

variable "storage_account_suffix" {
  description = "Unique suffix for the globally unique storage account name"
  type        = string
  default     = "01"
}