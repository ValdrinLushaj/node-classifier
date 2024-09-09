import boto3
import pytest
import json
from fastapi.testclient import TestClient
from lambdas.src.handlers.node_group import app
import os

client = TestClient(app)

@pytest.fixture(scope="session")
def dynamodb():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Use a separate table for testing
    test_table_name = 'NodeGroup_Test'
    
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
            {'AttributeName': 'Name', 'KeyType': 'HASH'},
            {'AttributeName': 'Class', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'Name', 'AttributeType': 'S'},
            {'AttributeName': 'Class', 'AttributeType': 'S'}
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

def test_create_node_group(dynamodb, prepare_data):
    node_group_data = {
        "name": "BT Base Server",
        "class_": "roles::base_server",
        "parameters": {"bt_product": "cea", "bt_tier": "nonprod"}
    }

    response = client.post("/nodegroup/", json=node_group_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()

    assert 'message' in data, \
        "Expected 'message' in response, got {}".format(data)
    assert data['message'] == 'Node Group created successfully', \
        f"Expected message 'Node Group created successfully', got '{data['message']}'"

def test_get_node_group(dynamodb, prepare_data):
    dynamodb.put_item(Item={
        'Name': 'BT Base Server',
        'Class': 'roles::base_server',
        'Parameters': '{"bt_product": "cea", "bt_tier": "nonprod"}'
    })

    response = client.get("/nodegroup/BT%20Base%20Server")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['Name'] == 'BT Base Server'
    assert data[0]['Class'] == 'roles::base_server'

def test_update_node_group(dynamodb, prepare_data):
    # Arrange: Create a node group directly in DynamoDB with correct keys
    dynamodb.put_item(Item={
        'Name': 'BT Base Server',
        'Class': 'roles::base_server',
        'Parameters': json.dumps({"bt_product": "cea", "bt_tier": "nonprod"})
    })

    # Prepare the updated data with correct keys
    updated_data = {
        "name": "BT Base Server",
        "class_": "roles::apache_server",
        "parameters": {"bt_product": "cea", "bt_tier": "pr"}
    }

    # Act: Update the node group
    response = client.put("/nodegroup/BT%20Base%20Server", json=updated_data)
    data = response.json()

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert data['message'] == 'Node Group updated successfully'

    # Verify the update in DynamoDB
    result = dynamodb.get_item(Key={
        'Name': 'BT Base Server',
        'Class': 'roles::apache_server'
    })
    assert 'Item' in result, "Expected item to be present in DynamoDB"
    assert result['Item']['Class'] == 'roles::apache_server'
    assert result['Item']['Parameters'] == json.dumps({"bt_product": "cea", "bt_tier": "pr"})

def test_delete_node_group(dynamodb, prepare_data):
    # Arrange:
    dynamodb.put_item(Item={
        'Name': 'BT Base Server',
        'Class': 'roles::base_server',
        'Parameters': '{"bt_product": "cea", "bt_tier": "nonprod"}'
    })

    # Act: Delete the node group
    response = client.delete("/nodegroup/BT%20Base%20Server")
    data = response.json()

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert data['message'] == 'Node group deleted successfully'

    # Verify the deletion in DynamoDB
    result = dynamodb.get_item(Key={
        'Name': 'BT%20Base%20Server',
        'Class': 'roles::base_server'
    })
    assert 'Item' not in result  # Ensure the item was deleted
