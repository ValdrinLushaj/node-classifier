data "aws_lambda_function" "node_handler" {
  function_name = aws_lambda_function.node_handler.function_name
  depends_on    = [aws_lambda_function.node_handler]
}

data "aws_lambda_function" "node_group_handler" {
  function_name = aws_lambda_function.node_group_handler.function_name
  depends_on    = [aws_lambda_function.node_group_handler]
}

data "aws_lambda_function" "environment_handler" {
  function_name = aws_lambda_function.environment_handler.function_name
  depends_on    = [aws_lambda_function.environment_handler]
}

data "aws_iam_policy_document" "api_gateway_policy" {
  statement {
    effect = "Allow"
    actions = [
      "execute-api:Invoke",
    ]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    resources = [
      "arn:aws:execute-api:us-east-1:767397798793:qps8kfvt6d/sandbox/*/*/*",
    ]

    condition {
      test     = "StringEquals"
      variable = "aws:SourceVpce"

      values = ["aws_vpc_endpoint.enc-vpc-endpoint.id"]
    }
  }
}


resource "aws_api_gateway_rest_api" "api" {
  name        = "NodeAPI"
  description = "API for accessing Node data"

  policy = data.aws_iam_policy_document.api_gateway_policy.json

  endpoint_configuration {
    types = ["PRIVATE"]
    vpc_endpoint_ids = [aws_vpc_endpoint.enc-vpc-endpoint.id]
  }
}

# resource "aws_api_gateway_method" "get_all_nodes" {
#   rest_api_id   = aws_api_gateway_rest_api.api.id
#   resource_id   = aws_api_gateway_resource.nodes.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

resource "aws_api_gateway_resource" "nodes" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "nodes"
}

resource "aws_api_gateway_resource" "unique_name" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.nodes.id
  path_part   = "{unique_name}"
}

# resource "aws_api_gateway_resource" "nodes_by_puppet_cluster" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_resource.nodes.id
#   path_part   = "puppet_cluster"
# }

# resource "aws_api_gateway_resource" "healthcheck" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_rest_api.api.root_resource_id
#   path_part   = "healthcheck"
# }

# resource "aws_api_gateway_resource" "nodes_by_puppet_cluster_name" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_resource.nodes_by_puppet_cluster.id
#   path_part   = "{puppet_cluster_name}"
# }

# resource "aws_api_gateway_resource" "hostgroup" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_resource.nodes.id
#   path_part   = "hostgroup"
# }

# resource "aws_api_gateway_resource" "hostgroup_name" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_resource.hostgroup.id
#   path_part   = "{node_group_name}"
# }

# resource "aws_api_gateway_resource" "nodes_by_environment" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_resource.nodes.id
#   path_part   = "environment"
# }

# resource "aws_api_gateway_resource" "nodes_by_environment_name" {
#   rest_api_id = aws_api_gateway_rest_api.api.id
#   parent_id   = aws_api_gateway_resource.nodes_by_environment.id
#   path_part   = "{environment_name}"
# }

resource "aws_api_gateway_resource" "nodegroup" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "nodegroup"
}

resource "aws_api_gateway_resource" "node_group_name" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.nodegroup.id
  path_part   = "{node_group_name}"
}

resource "aws_api_gateway_resource" "environment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "environment"
}

resource "aws_api_gateway_resource" "environment_name" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.environment.id
  path_part   = "{environment_name}"
}

resource "aws_api_gateway_resource" "puppet_cluster_name" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.environment_name.id
  path_part   = "{puppet_cluster_name}"
}

resource "aws_api_gateway_method" "get_node" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.unique_name.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "create_node" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.nodes.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "update_node" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.unique_name.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "delete_node" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.unique_name.id
  http_method   = "DELETE"
  authorization = "NONE"
}

# resource "aws_api_gateway_method" "get_nodes_by_puppet_cluster" {
#   rest_api_id   = aws_api_gateway_rest_api.api.id
#   resource_id   = aws_api_gateway_resource.nodes_by_puppet_cluster_name.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_method" "get_healthcheck" {
#   rest_api_id   = aws_api_gateway_rest_api.api.id
#   resource_id   = aws_api_gateway_resource.healthcheck.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_method" "get_nodes_by_hostgroup" {
#   rest_api_id   = aws_api_gateway_rest_api.api.id
#   resource_id   = aws_api_gateway_resource.hostgroup_name.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

# resource "aws_api_gateway_method" "get_nodes_by_environment" {
#   rest_api_id   = aws_api_gateway_rest_api.api.id
#   resource_id   = aws_api_gateway_resource.nodes_by_environment_name.id
#   http_method   = "GET"
#   authorization = "NONE"
# }

resource "aws_api_gateway_method" "get_nodegroup" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.node_group_name.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "create_nodegroup" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.nodegroup.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "update_nodegroup" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.node_group_name.id
  http_method   = "PUT"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "delete_nodegroup" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.node_group_name.id
  http_method   = "DELETE"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "get_environment" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.puppet_cluster_name.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "create_environment" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.environment.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "delete_environment" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.puppet_cluster_name.id
  http_method   = "DELETE"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_get_node" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.unique_name.id
  http_method             = aws_api_gateway_method.get_node.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.node_handler.invoke_arn
  depends_on              = [aws_lambda_function.node_handler]
}

resource "aws_api_gateway_integration" "lambda_create_node" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.nodes.id
  http_method             = aws_api_gateway_method.create_node.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.node_handler.invoke_arn
  depends_on              = [aws_lambda_function.node_handler]
}

resource "aws_api_gateway_integration" "lambda_update_node" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.unique_name.id
  http_method             = aws_api_gateway_method.update_node.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.node_handler.invoke_arn
  depends_on              = [aws_lambda_function.node_handler]
}

resource "aws_api_gateway_integration" "lambda_delete_node" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.unique_name.id
  http_method             = aws_api_gateway_method.delete_node.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.node_handler.invoke_arn
  depends_on              = [aws_lambda_function.node_handler]
}

# resource "aws_api_gateway_integration" "lambda_get_all_nodes" {
#   rest_api_id             = aws_api_gateway_rest_api.api.id
#   resource_id             = aws_api_gateway_resource.nodes.id
#   http_method             = aws_api_gateway_method.get_all_nodes.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = data.aws_lambda_function.node_handler.invoke_arn
#   depends_on              = [aws_lambda_function.node_handler]
# }

# resource "aws_api_gateway_integration" "lambda_get_healthcheck" {
#   rest_api_id             = aws_api_gateway_rest_api.api.id
#   resource_id             = aws_api_gateway_resource.healthcheck.id
#   http_method             = aws_api_gateway_method.get_healthcheck.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = data.aws_lambda_function.node_handler.invoke_arn
#   depends_on              = [aws_lambda_function.node_handler]
# }

# resource "aws_api_gateway_integration" "lambda_get_nodes_by_puppet_cluster" {
#   rest_api_id             = aws_api_gateway_rest_api.api.id
#   resource_id             = aws_api_gateway_resource.nodes_by_puppet_cluster_name.id
#   http_method             = aws_api_gateway_method.get_nodes_by_puppet_cluster.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = data.aws_lambda_function.node_handler.invoke_arn
#   depends_on              = [aws_lambda_function.node_handler]
# }

# resource "aws_api_gateway_integration" "lambda_get_nodes_by_hostgroup" {
#   rest_api_id             = aws_api_gateway_rest_api.api.id
#   resource_id             = aws_api_gateway_resource.hostgroup_name.id
#   http_method             = aws_api_gateway_method.get_nodes_by_hostgroup.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = data.aws_lambda_function.node_handler.invoke_arn
#   depends_on              = [aws_lambda_function.node_handler]
# }

# resource "aws_api_gateway_integration" "lambda_get_nodes_by_environment" {
#   rest_api_id             = aws_api_gateway_rest_api.api.id
#   resource_id             = aws_api_gateway_resource.nodes_by_environment_name.id
#   http_method             = aws_api_gateway_method.get_nodes_by_environment.http_method
#   integration_http_method = "POST"
#   type                    = "AWS_PROXY"
#   uri                     = data.aws_lambda_function.node_handler.invoke_arn
#   depends_on              = [aws_lambda_function.node_handler]
# }

resource "aws_api_gateway_integration" "lambda_get_nodegroup" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.node_group_name.id
  http_method             = aws_api_gateway_method.get_nodegroup.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.node_group_handler.invoke_arn
  depends_on              = [aws_lambda_function.node_group_handler]
}

resource "aws_api_gateway_integration" "lambda_create_nodegroup" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.nodegroup.id
  http_method             = aws_api_gateway_method.create_nodegroup.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.node_group_handler.invoke_arn
  depends_on              = [aws_lambda_function.node_group_handler]
}

resource "aws_api_gateway_integration" "lambda_update_nodegroup" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.node_group_name.id
  http_method             = aws_api_gateway_method.update_nodegroup.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.node_group_handler.invoke_arn
  depends_on              = [aws_lambda_function.node_group_handler]
}

resource "aws_api_gateway_integration" "lambda_delete_nodegroup" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.node_group_name.id
  http_method             = aws_api_gateway_method.delete_nodegroup.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.node_group_handler.invoke_arn
  depends_on              = [aws_lambda_function.node_group_handler]
}

resource "aws_api_gateway_integration" "lambda_get_environment" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.puppet_cluster_name.id
  http_method             = aws_api_gateway_method.get_environment.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.environment_handler.invoke_arn
  depends_on              = [aws_lambda_function.environment_handler]
}

resource "aws_api_gateway_integration" "lambda_create_environment" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.environment.id
  http_method             = aws_api_gateway_method.create_environment.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.environment_handler.invoke_arn
  depends_on              = [aws_lambda_function.environment_handler]
}

resource "aws_api_gateway_integration" "lambda_delete_environment" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.puppet_cluster_name.id
  http_method             = aws_api_gateway_method.delete_environment.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.environment_handler.invoke_arn
  depends_on              = [aws_lambda_function.environment_handler]
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "sandbox"
  depends_on  = [
    aws_api_gateway_integration.lambda_get_node,
    aws_api_gateway_integration.lambda_create_node,
    aws_api_gateway_integration.lambda_update_node,
    aws_api_gateway_integration.lambda_delete_node,
    # aws_api_gateway_integration.lambda_get_all_nodes,
    # aws_api_gateway_integration.lambda_get_healthcheck,
    # aws_api_gateway_integration.lambda_get_nodes_by_puppet_cluster,
    # aws_api_gateway_integration.lambda_get_nodes_by_hostgroup,
    # aws_api_gateway_integration.lambda_get_nodes_by_environment,
    aws_api_gateway_integration.lambda_get_nodegroup,
    aws_api_gateway_integration.lambda_create_nodegroup,
    aws_api_gateway_integration.lambda_update_nodegroup,
    aws_api_gateway_integration.lambda_delete_nodegroup,
    aws_api_gateway_integration.lambda_get_environment,
    aws_api_gateway_integration.lambda_create_environment,
    aws_api_gateway_integration.lambda_delete_environment
  ]
}

resource "aws_lambda_permission" "apigw_lambda_node" {
  statement_id  = "AllowAPIGatewayInvokeNode"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.node_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
  depends_on    = [aws_lambda_function.node_handler]
}

resource "aws_lambda_permission" "apigw_lambda_node_group" {
  statement_id  = "AllowAPIGatewayInvokeNodeGroup"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.node_group_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
  depends_on    = [aws_lambda_function.node_group_handler]
}

resource "aws_lambda_permission" "apigw_lambda_environment" {
  statement_id  = "AllowAPIGatewayInvokeEnvironment"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.environment_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
  depends_on    = [aws_lambda_function.environment_handler]
}

# resource "aws_lambda_permission" "apigw_lambda_healthcheck" {
#   statement_id  = "AllowAPIGatewayInvokeHealthCheck"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.node_handler.function_name
#   principal     = "apigateway.amazonaws.com"
#   source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
#   depends_on    = [aws_lambda_function.node_handler]
# }
