data "aws_iam_role" "lambda_exec" {
  name = "LambdaDdbPost"
}

locals {
  python_version = "python3.9"
  type           = "zip" 
}

# Node handler
resource "local_file" "lambda_python_code_node" {
  content  = file("${path.module}/lambdas/src/handlers/node.py")
  filename = "${path.module}/lambdas/src/handlers/node.py"
}

data "archive_file" "lambda_zip_node" {
  type        = local.type
  source_file = "${path.module}/lambdas/src/handlers/node.py"
  output_path = "${path.module}/node_lambda_function_src.zip"
}

resource "aws_lambda_function" "node_handler" {
  function_name    = "nodeHandler"
  filename         = data.archive_file.lambda_zip_node.output_path
  description      = "Handle CRUD operations on Node data in DynamoDB using FastAPI"
  runtime          = local.python_version
  handler          = "node.handler"
  source_code_hash = data.archive_file.lambda_zip_node.output_base64sha256
  role             = data.aws_iam_role.lambda_exec.arn
  depends_on       = [local_file.lambda_python_code_node]
}

# Node group handler
resource "local_file" "lambda_python_code_node_group" {
  content  = file("${path.module}/lambdas/src/handlers/node_group.py")
  filename = "${path.module}/lambdas/src/handlers/node_group.py"
}

data "archive_file" "lambda_zip_node_group" {
  type        = local.type
  source_file = "${path.module}/lambdas/src/handlers/node_group.py"
  output_path = "${path.module}/node_group_lambda_function_src.zip"
}

resource "aws_lambda_function" "node_group_handler" {
  function_name    = "nodeGroupHandler"
  filename         = data.archive_file.lambda_zip_node_group.output_path
  description      = "Handle CRUD operations on Node Group data in DynamoDB using FastAPI"
  runtime          = local.python_version
  handler          = "node_group.handler"
  source_code_hash = data.archive_file.lambda_zip_node_group.output_base64sha256
  role             = data.aws_iam_role.lambda_exec.arn
  depends_on       = [local_file.lambda_python_code_node_group]
}

# Environment handler
resource "local_file" "lambda_python_code_environment" {
  content  = file("${path.module}/lambdas/src/handlers/environment.py")
  filename = "${path.module}/lambdas/src/handlers/environment.py"
}

data "archive_file" "lambda_zip_environment" {
  type        = local.type
  source_file = "${path.module}/lambdas/src/handlers/environment.py"
  output_path = "${path.module}/environment_lambda_function_src.zip"
}

resource "aws_lambda_function" "environment_handler" {
  function_name    = "environmentHandler"
  filename         = data.archive_file.lambda_zip_environment.output_path
  description      = "Handle CRUD operations on Environment data in DynamoDB using FastAPI"
  runtime          = local.python_version
  handler          = "environment.handler"
  source_code_hash = data.archive_file.lambda_zip_environment.output_base64sha256
  role             = data.aws_iam_role.lambda_exec.arn
  depends_on       = [local_file.lambda_python_code_environment]
}