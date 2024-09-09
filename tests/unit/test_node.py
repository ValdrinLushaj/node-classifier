import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from boto3.dynamodb.conditions import Key

# Import the FastAPI app
from lambdas.src.handlers.node import app

# Create a TestClient for the FastAPI app
client = TestClient(app)

@pytest.fixture(scope='function')
def mock_dynamodb():
    # Patch the node_table used in the node_handler module
    with patch('lambdas.src.handlers.node.node_table') as mock_table:
        yield mock_table

def test_healthcheck():
    # Act
    response = client.get("/healthcheck")

    # Assert
    assert response.status_code == 200, \
        "Healthcheck: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"status": "ok"}, \
        "Healthcheck: Expected response body {'status': 'ok'}, got {}".format(response.json())

def test_create_node(mock_dynamodb):
    # Arrange
    # Mock DynamoDB responses
    mock_dynamodb.query.return_value = {'Items': []}  # Node does not exist
    mock_dynamodb.put_item.return_value = {}  # Mimic DynamoDB's response

    # Prepare the mock data for the node
    node_data = {
        'unique_name': 'us01vlbase01.saas-n.com',
        'node_group_name': 'BT Base Server',
        'environment_name': 'master',
        'puppet_cluster_name': 'ny2-saas-n'
    }

    # Act
    response = client.post("/nodes/", json=node_data)

    # Assert
    assert response.status_code == 200, \
        "Create Node: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"message": "Node created successfully"}, \
        "Create Node: Expected message 'Node created successfully', got '{}'".format(response.json())

    mock_dynamodb.put_item.assert_called_once_with(Item={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Base Server',
        'environment_name': 'master',
        'puppet_cluster_name': 'ny2-saas-n'
    })

def test_read_node(mock_dynamodb):
    # Arrange
    # Mock the return value for query
    mock_dynamodb.query.return_value = {
        'Items': [{'UniqueName': 'us01vlbase01.saas-n.com', 'NodeGroupName': 'BT Base Server'}]
    }

    # Act
    response = client.get("/nodes/us01vlbase01.saas-n.com")

    # Assert
    assert response.status_code == 200, \
        "Read Node: Expected status code 200, got {}".format(response.status_code)
    assert response.json()[0]['UniqueName'] == 'us01vlbase01.saas-n.com', \
        "Read Node: Expected 'UniqueName' to be 'us01vlbase01.saas-n.com', got '{}'".format(response.json()[0]['UniqueName'])

    mock_dynamodb.query.assert_called_once_with(
        KeyConditionExpression=Key('UniqueName').eq('us01vlbase01.saas-n.com')
    )

def test_update_node(mock_dynamodb):
    # Arrange
    # Mock the return value for query
    mock_dynamodb.query.return_value = {
        'Items': [{'UniqueName': 'us01vlbase01.saas-n.com', 'NodeGroupName': 'BT Base Server', 'environment_name': 'master', 'puppet_cluster_name': 'ny2-saas-n'}]
    }

    # Prepare the mock data for updating the node
    updated_node_data = {
        'unique_name': 'us01vlbase01.saas-n.com',
        'node_group_name': 'BT Apache Server',
        'environment_name': 'production',
        'puppet_cluster_name': 'ny2-saas-n'
    }

    # Act
    response = client.put("/nodes/us01vlbase01.saas-n.com", json=updated_node_data)

    # Assert
    assert response.status_code == 200, \
        "Update Node: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"message": "Node updated successfully"}, \
        "Update Node: Expected message 'Node updated successfully', got '{}'".format(response.json())

    mock_dynamodb.delete_item.assert_called_once_with(Key={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Base Server'
    })
    mock_dynamodb.put_item.assert_called_once_with(Item={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Apache Server',
        'environment_name': 'production',
        'puppet_cluster_name': 'ny2-saas-n'
    })

def test_delete_node(mock_dynamodb):
    # Arrange
    # Mock the return value for query
    mock_dynamodb.query.return_value = {
        'Items': [{'UniqueName': 'us01vlbase01.saas-n.com', 'NodeGroupName': 'BT Apache Server'}]
    }

    # Act
    response = client.delete("/nodes/us01vlbase01.saas-n.com")

    # Assert
    assert response.status_code == 200, \
        "Delete Node: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"message": "Node deleted successfully"}, \
        "Delete Node: Expected message 'Node deleted successfully', got '{}'".format(response.json())

    mock_dynamodb.delete_item.assert_called_once_with(
        Key={'UniqueName': 'us01vlbase01.saas-n.com', 'NodeGroupName': 'BT Apache Server'}
    )
