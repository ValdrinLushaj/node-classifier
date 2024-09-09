import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from boto3.dynamodb.conditions import Key
from lambdas.src.handlers.node_group import app

# Initialize the TestClient with FastAPI app
client = TestClient(app)

@pytest.fixture(scope='function')
def mock_dynamodb():
    # Patch the node_group_table used in the FastAPI module
    with patch('lambdas.src.handlers.node_group.node_group_table') as mock_table:
        yield mock_table

def test_healthcheck():
    # Act
    response = client.get("/healthcheck")

    # Assert
    assert response.status_code == 200, \
        "Healthcheck: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"status": "ok"}, \
        "Healthcheck: Expected response body {'status': 'ok'}, got {}".format(response.json())

def test_create_node_group(mock_dynamodb):
    # Arrange
    node_group_data = {
        'name': 'BT Base Server',
        'class_': 'roles::base_server',
        'parameters': {'bt_product': 'cea'}
    }

    # Mock DynamoDB responses
    mock_dynamodb.query.return_value = {'Items': []}  # Node group does not exist
    mock_dynamodb.put_item.return_value = {}  # Mimic DynamoDB's response

    # Act
    response = client.post("/nodegroup/", json=node_group_data)

    # Assert
    assert response.status_code == 200, \
        "Create Node Group: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"message": "Node Group created successfully"}, \
        "Create Node Group: Expected message 'Node Group created successfully', got '{}'".format(response.json())

    # Ensure that put_item was called with the correct arguments
    mock_dynamodb.put_item.assert_called_once_with(Item={
        'Name': 'BT Base Server',
        'Class': 'roles::base_server',
        'Parameters': json.dumps({'bt_product': 'cea'})
    })

def test_read_node_group(mock_dynamodb):
    # Arrange
    # Mock the return value for query
    mock_dynamodb.query.return_value = {
        'Items': [{'Name': 'BT Base Server', 'Class': 'roles::base_server'}]
    }

    # Act
    response = client.get("/nodegroup/BT%20Base%20Server")

    # Assert
    assert response.status_code == 200, \
        "Read Node Group: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == [{'Name': 'BT Base Server', 'Class': 'roles::base_server'}], \
        "Read Node Group: Expected response body [{'Name': 'BT Base Server', 'Class': 'roles::base_server'}], got {}".format(response.json())

    # Ensure that query was called with the correct arguments
    mock_dynamodb.query.assert_called_once_with(
        KeyConditionExpression=Key('Name').eq('BT Base Server')
    )

def test_update_node_group(mock_dynamodb):
    # Arrange
    # Mock the return value for query
    mock_dynamodb.query.return_value = {
        'Items': [{'Name': 'BT Base Server', 'Class': 'roles::base_server', 'Parameters': json.dumps({'bt_product': 'cea'})}]
    }

    updated_data = {
        'name': 'BT Base Server',
        'class_': 'roles::apache_server',
        'parameters': {
            'bt_product': 'cea',
            'bt_role': 'apache'
        }
    }

    # Act
    response = client.put("/nodegroup/BT%20Base%20Server", json=updated_data)

    # Assert
    assert response.status_code == 200, \
        "Update Node Group: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"message": "Node Group updated successfully"}, \
        "Update Node Group: Expected message 'Node Group updated successfully', got '{}'".format(response.json())

    # Ensure that delete_item and put_item were called with the correct arguments
    mock_dynamodb.delete_item.assert_called_once_with(Key={
        'Name': 'BT Base Server',
        'Class': 'roles::base_server'
    })
    mock_dynamodb.put_item.assert_called_once_with(Item={
        'Name': 'BT Base Server',
        'Class': 'roles::apache_server',
        'Parameters': json.dumps({
            'bt_product': 'cea',
            'bt_role': 'apache'
        })
    })

def test_delete_node_group(mock_dynamodb):
    # Arrange
    # Mock the return value for query
    mock_dynamodb.query.return_value = {
        'Items': [{'Name': 'BT Base Server', 'Class': 'roles::apache_server', 'Parameters': json.dumps({'bt_product': 'cea', 'bt_role': 'apache'})}]
    }

    # Act
    response = client.delete("/nodegroup/BT%20Base%20Server")

    # Assert
    assert response.status_code == 200, \
        "Delete Node Group: Expected status code 200, got {}".format(response.status_code)
    assert response.json() == {"message": "Node group deleted successfully"}, \
        "Delete Node Group: Expected message 'Node group deleted successfully', got '{}'".format(response.json())

    # Ensure that delete_item was called with the correct arguments
    mock_dynamodb.delete_item.assert_called_once_with(
        Key={'Name': 'BT Base Server', 'Class': 'roles::apache_server'}
    )
