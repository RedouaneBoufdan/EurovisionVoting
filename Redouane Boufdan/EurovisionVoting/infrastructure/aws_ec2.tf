terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "eurovision_worker" {
  ami           = "ami-xxxxxxxxxxxxxxxxx" # replace with a valid Ubuntu AMI
  instance_type = var.aws_instance_type

  tags = {
    Name    = "eurovision-aws-worker"
    Project = "EurovisionVoting"
  }
}
