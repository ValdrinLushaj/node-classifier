External Node Classifier
Overview

The External Node Classifier project is designed to manage nodes, node groups, and environments in a cloud-native infrastructure. This system uses AWS Lambda, FastAPI, and DynamoDB to create a serverless architecture that is scalable and efficient. The project is primarily written in Python and is deployed using Terraform for Infrastructure as Code (IaC). The CI/CD pipeline is managed via GitLab CI/CD, ensuring that the project is continuously tested and deployed.
Project Structure

The project is organized into several key directories and files:

    lambdas/src/handlers/: Contains the FastAPI-based Lambda functions.
    terraform/: Contains Terraform configuration files for provisioning the necessary AWS resources.
    tests/: Contains unit and integration tests for the Lambda functions.
    .gitlab-ci.yml: CI/CD pipeline configuration for GitLab.

Lambda Handlers

There are three main Lambda handlers, each corresponding to a different aspect of the node classification system:

    node.py
        Handles CRUD operations for individual nodes.
        Routes:
            POST /nodes/: Create a new node.
            GET /nodes/{unique_name}: Retrieve a node by its unique name.
            PUT /nodes/{unique_name}: Update an existing node.
            DELETE /nodes/{unique_name}: Delete a node by its unique name.
        DynamoDB Table: Node

    node_group.py
        Handles CRUD operations for node groups.
        Routes:
            POST /nodegroup/: Create a new node group.
            GET /nodegroup/{node_group_name}: Retrieve a node group by its name.
            PUT /nodegroup/{node_group_name}: Update an existing node group.
            DELETE /nodegroup/{node_group_name}: Delete a node group by its name.
        DynamoDB Table: NodeGroup

    environment.py
        Handles CRUD operations for environments.
        Routes:
            POST /environment/: Create a new environment.
            GET /environment/{environment_name}/{puppet_cluster_name}: Retrieve an environment by its name and Puppet cluster.
            DELETE /environment/{environment_name}/{puppet_cluster_name}: Delete an environment by its name and Puppet cluster.
        DynamoDB Table: Environment

Terraform Configuration

The Terraform configuration files manage the deployment of AWS resources, including Lambda functions, API Gateway, and DynamoDB tables.

    main.tf: Defines the AWS provider and remote backend for storing Terraform state.
    lambda.tf: Provisions the Lambda functions and IAM roles.
    api-gw.tf: Configures the API Gateway and integrates it with the Lambda functions.
    dynamodb.tf: Sets up the DynamoDB tables used by the application.

CI/CD Pipeline

The CI/CD pipeline is defined in the .gitlab-ci.yml file. The pipeline has the following stages:

    Plan: Runs terraform plan to generate an execution plan for Terraform changes.
    Package: Packages the Lambda functions as ZIP files.
    Test: Runs unit tests to ensure code quality.
    Integration: Runs integration tests to verify the interaction between Lambda functions and AWS resources.
    Apply: Applies the Terraform plan to deploy changes to the AWS environment.

Tests

The tests directory contains:

    Unit Tests: These tests validate individual functions within the Lambda handlers.
    Integration Tests: These tests validate the end-to-end functionality of the API routes and their interaction with DynamoDB.

## <span style="color:green"> Contributing

Thank you for showing interest in contributing! Below are some instructions.

- [ ] Clone this repository and branch this project repo.
- [ ] Create a merge request and inspect the Terraform plan under 'Build/pipelines'. The Terraform plan compares your code with the existing state.
- [ ] Merging the MR that you are currently working on, it will run a deploy which runs a build and then applies the plan.

## <span style="color:green"> Commit and Branch Format
Commits must conform to the conventional commits format with a Jira ticket reference in the parentheses. The "type" component of the message must be either feat (for a new feature), fix (for any fix to existing functionality) or chore (for any non-impacting administrative code change). To enable accountability, the "scope" component of the conventional commit message must contain a valid Jira ticket ID.

Example valid commit messages:
```bash
# A valid feature commit message
git commit -m 'feat(CPE-0000): Example commit mesage'
```

## <span style="color:green"> Support
Please create a CPE ticket for External Node Classifier - ENC support.