# DynamoDB Table: environments
resource "aws_dynamodb_table" "environments" {
  name         = "Environment"
  billing_mode = "PROVISIONED"
  hash_key     = "EnvironmentName"
  range_key    = "PuppetClusterName"

  attribute {
    name = "EnvironmentName"
    type = "S"
  }

  attribute {
    name = "PuppetClusterName"
    type = "S"
  }

  tags = {
    Name        = "Environments"
    Environment = "Production"
  }

  read_capacity  = 5
  write_capacity = 5
}

# Auto Scaling for Read Capacity (environments table)
resource "aws_appautoscaling_target" "dynamodb_env_read_target" {
  max_capacity       = 40
  min_capacity       = 8
  resource_id        = "table/Environment"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_env_read_policy" {
  name               = "DynamoDBEnvReadScalingPolicy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_env_read_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_env_read_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_env_read_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }

    target_value = 70.0
  }
}

# Auto Scaling for Write Capacity (environments table)
resource "aws_appautoscaling_target" "dynamodb_env_write_target" {
  max_capacity       = 20
  min_capacity       = 4
  resource_id        = "table/Environment"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_env_write_policy" {
  name               = "DynamoDBEnvWriteScalingPolicy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_env_write_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_env_write_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_env_write_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }

    target_value = 70.0
  }
}

# DynamoDB Table: node_group
resource "aws_dynamodb_table" "node_group" {
  name         = "NodeGroup"
  billing_mode = "PROVISIONED"
  hash_key     = "Name"
  range_key    = "Class"

  attribute {
    name = "Name"
    type = "S"
  }

  attribute {
    name = "Class"
    type = "S"
  }

  attribute {
    name = "Parameters"
    type = "S"
  }

  local_secondary_index {
    name               = "ParametersIndex"
    range_key          = "Parameters"
    projection_type    = "INCLUDE"
    non_key_attributes = ["Name"]
  }

  tags = {
    Name        = "NodeGroup"
    Environment = "Production"
  }

  read_capacity  = 5
  write_capacity = 5
}

# Auto Scaling for Read Capacity (node_group table)
resource "aws_appautoscaling_target" "dynamodb_nodegroup_read_target" {
  max_capacity       = 40
  min_capacity       = 8
  resource_id        = "table/NodeGroup"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_nodegroup_read_policy" {
  name               = "DynamoDBNodeGroupReadScalingPolicy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_nodegroup_read_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_nodegroup_read_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_nodegroup_read_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }

    target_value = 70.0
  }
}

# Auto Scaling for Write Capacity (node_group table)
resource "aws_appautoscaling_target" "dynamodb_nodegroup_write_target" {
  max_capacity       = 20
  min_capacity       = 4
  resource_id        = "table/NodeGroup"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_nodegroup_write_policy" {
  name               = "DynamoDBNodeGroupWriteScalingPolicy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_nodegroup_write_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_nodegroup_write_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_nodegroup_write_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }

    target_value = 70.0
  }
}

# DynamoDB Table: node
resource "aws_dynamodb_table" "node" {
  name         = "Node"
  billing_mode = "PROVISIONED"
  hash_key     = "UniqueName"
  range_key    = "NodeGroupName"

  attribute {
    name = "UniqueName"
    type = "S"
  }

  attribute {
    name = "NodeGroupName"
    type = "S"
  }

  attribute {
    name = "EnvironmentName"
    type = "S"
  }

  attribute {
    name = "PuppetClusterName"
    type = "S"
  }

  local_secondary_index {
    name               = "EnvironmentIndex"
    range_key          = "EnvironmentName"
    projection_type    = "INCLUDE"
    non_key_attributes = ["NodeGroupID"]
  }

  local_secondary_index {
    name               = "PuppetClusterIndex"
    range_key          = "PuppetClusterName"
    projection_type    = "INCLUDE"
    non_key_attributes = ["NodeGroupID"]
  }

  tags = {
    Name        = "Node"
    Environment = "Production"
  }

  read_capacity  = 5
  write_capacity = 5
}

# Auto Scaling for Read Capacity (node table)
resource "aws_appautoscaling_target" "dynamodb_node_read_target" {
  max_capacity       = 40
  min_capacity       = 8
  resource_id        = "table/Node"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_node_read_policy" {
  name               = "DynamoDBNodeReadScalingPolicy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_node_read_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_node_read_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_node_read_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }

    target_value = 70.0
  }
}

# Auto Scaling for Write Capacity (node table)
resource "aws_appautoscaling_target" "dynamodb_node_write_target" {
  max_capacity       = 20
  min_capacity       = 4
  resource_id        = "table/Node"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "dynamodb_node_write_policy" {
  name               = "DynamoDBNodeWriteScalingPolicy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dynamodb_node_write_target.resource_id
  scalable_dimension = aws_appautoscaling_target.dynamodb_node_write_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dynamodb_node_write_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }

    target_value = 70.0
  }
}