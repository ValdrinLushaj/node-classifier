import boto3
import pytest
from fastapi.testclient import TestClient
from lambdas.src.handlers.node import app, node_table
import os

# Create a TestClient for the FastAPI app
client = TestClient(app)

@pytest.fixture(scope="session")
def dynamodb():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Use a separate table for testing
    test_table_name = 'Node_Test'
    
    # Check if the test table already exists
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    if test_table_name in existing_tables:
        table = dynamodb.Table(test_table_name)
        table.delete()
        table.meta.client.get_waiter('table_not_exists').wait(TableName=test_table_name)
    
    # Create the test table
    table = dynamodb.create_table(
        TableName=test_table_name,
        KeySchema=[
            {'AttributeName': 'UniqueName', 'KeyType': 'HASH'},
            {'AttributeName': 'NodeGroupName', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'UniqueName', 'AttributeType': 'S'},
            {'AttributeName': 'NodeGroupName', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    # Wait for the table to be created and active
    table.meta.client.get_waiter('table_exists').wait(TableName=test_table_name)
    
    # Set the table name in the handler to the test table
    os.environ['DYNAMODB_TABLE_NAME'] = test_table_name

    yield table

    # Cleanup: delete the table after all tests
    table.delete()
    table.meta.client.get_waiter('table_not_exists').wait(TableName=test_table_name)

@pytest.fixture(scope="function")
def prepare_data(dynamodb):
    # This fixture is to clean up the table between tests
    dynamodb.scan()['Items'].clear()

def test_create_node(dynamodb, prepare_data):
    node_data = {
        "unique_name": "us01vlbase01.saas-n.com",
        "node_group_name": "BT Base Server",
        "environment_name": "master",
        "puppet_cluster_name": "ny2-saas-n"
    }

    response = client.post("/nodes/", json=node_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()

    # Assert that the response is as expected
    assert 'message' in data, \
        "Expected 'message' in response, got {}".format(data)
    assert data['message'] == 'Node created successfully', \
        f"Expected message 'Node created successfully', got '{data['message']}'"

    # Verify the item was added to DynamoDB
    result = dynamodb.get_item(Key={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Base Server'
    })
    assert 'Item' in result, "Expected item to be present in DynamoDB"
    assert result['Item']['UniqueName'] == 'us01vlbase01.saas-n.com', \
        f"Expected 'UniqueName' to be 'us01vlbase01.saas-n.com', got {result['Item']['UniqueName']}"
    assert result['Item']['NodeGroupName'] == 'BT Base Server', \
        f"Expected 'NodeGroupName' to be 'BT Base Server', got {result['Item']['NodeGroupName']}"

def test_get_node(dynamodb, prepare_data):
    # Arrange: create a node directly in DynamoDB with correct keys
    dynamodb.put_item(Item={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Base Server',
        'environment_name': 'master',
        'puppet_cluster_name': 'ny2-saas-n'
    })

    # Act: retrieve the node
    response = client.get("/nodes/us01vlbase01.saas-n.com")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['UniqueName'] == 'us01vlbase01.saas-n.com'
    assert data[0]['NodeGroupName'] == 'BT Base Server'

def test_update_node(dynamodb, prepare_data):
    # Arrange: create a node directly in DynamoDB with correct keys
    dynamodb.put_item(Item={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Base Server',
        'environment_name': 'master',
        'puppet_cluster_name': 'ny2-saas-n'
    })

    # Prepare the updated data with the correct keys
    updated_data = {
        'unique_name': 'us01vlbase01.saas-n.com',
        'node_group_name': 'BT Apache Server',
        'environment_name': 'production',
        'puppet_cluster_name': 'ny2-saas-n'
    }

    # Act: update the node
    response = client.put("/nodes/us01vlbase01.saas-n.com", json=updated_data)
    data = response.json()

    # Assert
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert data['message'] == 'Node updated successfully', f"Expected message 'Node updated successfully', got '{data['message']}'"

    # Verify the update in DynamoDB
    result = dynamodb.get_item(Key={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Apache Server'
    })
    assert 'Item' in result, "Expected item to be present in DynamoDB"
    assert result['Item']['environment_name'] == 'production', f"Expected 'environment_name' to be 'production', got {result['Item']['environment_name']}"
    assert result['Item']['puppet_cluster_name'] == 'ny2-saas-n', f"Expected 'puppet_cluster_name' to be 'ny2-saas-n', got {result['Item']['puppet_cluster_name']}"

def test_delete_node(dynamodb, prepare_data):
    # Arrange: create a node directly in DynamoDB with correct keys
    dynamodb.put_item(Item={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Apache Server',
        'environment_name': 'production',
        'puppet_cluster_name': 'ny2-saas-n'
    })

    # Act: delete the node
    response = client.delete("/nodes/us01vlbase01.saas-n.com")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data['message'] == 'Node deleted successfully'

    # Verify the deletion in DynamoDB
    result = dynamodb.get_item(Key={
        'UniqueName': 'us01vlbase01.saas-n.com',
        'NodeGroupName': 'BT Apache Server'
    })
    assert 'Item' not in result
