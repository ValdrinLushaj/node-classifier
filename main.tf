terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0"
    }
  }

  backend "s3" {
    bucket = "lob-bt-terraform-backend-state"
    key    = "aws-node-classifier-state/state.tf"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}
