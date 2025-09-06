variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Name prefix for resources"
  type        = string
  default     = "lu-jenkins-advanced"
}

variable "instance_type" {
  description = "EC2 size for Jenkins"
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "EC2 key pair name"
  type        = string
}

variable "allowed_cidrs" {
  description = "CIDRs allowed to access SSH (22) and Jenkins (8080)"
  type        = list(string)
}