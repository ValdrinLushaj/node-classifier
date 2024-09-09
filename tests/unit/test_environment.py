import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from boto3.dynamodb.conditions import Key
from lambdas.src.handlers.environment import app

# Initialize the TestClient with FastAPI app
client = TestClient(app)

@pytest.fixture(scope='function')
def mock_dynamodb():
    # Patch the environment_table used in the FastAPI module
    with patch('lambdas.src.handlers.environment.environment_table') as mock_table:
        yield mock_table

def test_healthcheck():
    # Act
    response = client.get("/healthcheck")

    # Assert
    assert response.status_code == 200, \
        "Healthcheck: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"status": "ok"}, \
        "Healthcheck: Expected response body {'status': 'ok'}, got {}".format(response.json())

def test_create_environment(mock_dynamodb):
    # Arrange
    environment_data = {
        'environment_name': 'master',
        'puppet_cluster_name': 'ny2-saas-n'
    }

    # Mock DynamoDB responses
    mock_dynamodb.put_item.return_value = {}  # Mimic DynamoDB's response

    # Act
    response = client.post("/environment/", json=environment_data)

    # Assert
    assert response.status_code == 200, \
        "Create Environment: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"message": "Environment created successfully"}, \
        "Create Environment: Expected message 'Environment created successfully', got '{}'".format(response.json())

    # Ensure that put_item was called with the correct arguments
    mock_dynamodb.put_item.assert_called_once_with(Item={
        'EnvironmentName': 'master',
        'PuppetClusterName': 'ny2-saas-n'
    })

def test_read_environment(mock_dynamodb):
    # Arrange
    # Mock the return value for query
    mock_dynamodb.query.return_value = {
        'Items': [{'EnvironmentName': 'master', 'PuppetClusterName': 'ny2-saas-n'}]
    }

    # Act
    response = client.get("/environment/master/ny2-saas-n")

    # Assert
    assert response.status_code == 200, \
        "Read Environment: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == [{'EnvironmentName': 'master', 'PuppetClusterName': 'ny2-saas-n'}], \
        "Read Environment: Expected response body [{'EnvironmentName': 'master', 'PuppetClusterName': 'ny2-saas-n'}], got {}".format(response.json())

    # Ensure that query was called with the correct arguments
    mock_dynamodb.query.assert_called_once_with(
        KeyConditionExpression=Key('EnvironmentName').eq('master') & Key('PuppetClusterName').eq('ny2-saas-n')
    )

def test_delete_environment(mock_dynamodb):
    # Arrange
    # Mock the return value for delete_item
    mock_dynamodb.delete_item.return_value = {}

    # Act
    response = client.delete("/environment/master/ny2-saas-n")

    # Assert
    assert response.status_code == 200, \
        "Delete Environment: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"message": "Environment deleted successfully"}, \
        "Delete Environment: Expected message 'Environment deleted successfully', got '{}'".format(response.json())

    # Ensure that delete_item was called with the correct arguments
    mock_dynamodb.delete_item.assert_called_once_with(
        Key={'EnvironmentName': 'master', 'PuppetClusterName': 'ny2-saas-n'}
    )
