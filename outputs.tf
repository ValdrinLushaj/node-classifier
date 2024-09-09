output "environments_table_name" {
  description = "The name of the Environments DynamoDB table"
  value       = aws_dynamodb_table.environments.name
}

output "node_group_table_name" {
  description = "The name of the Node Group DynamoDB table"
  value       = aws_dynamodb_table.node_group.name
}

output "node_table_name" {
  description = "The name of the Node DynamoDB table"
  value       = aws_dynamodb_table.node.name
}

output "vpc_endpoint_id" {
  value = aws_vpc_endpoint.enc-vpc-endpoint.id
  description = "The ID of the VPC endpoint"
}

output "private-vpc-SG" {
  value = aws_security_group.private-vpc-SG.id
  description = "The ID of the VPC endpoint"
}

