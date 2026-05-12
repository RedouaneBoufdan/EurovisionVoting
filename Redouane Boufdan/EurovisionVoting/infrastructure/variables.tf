variable "aws_region" {
  description = "AWS region for the cloud datacenter"
  type        = string
  default     = "eu-central-1"
}

variable "aws_instance_type" {
  description = "Instance type for AWS workers"
  type        = string
  default     = "t3.small"
}

variable "proxmox_node" {
  description = "Proxmox node name"
  type        = string
  default     = "pve"
}
