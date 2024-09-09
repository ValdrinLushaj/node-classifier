import boto3
import pytest
from fastapi.testclient import TestClient
from lambdas.src.handlers.environment import app, environment_table
import os

client = TestClient(app)

@pytest.fixture(scope="session")
def dynamodb():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    test_table_name = 'Environment_Test'
    
    existing_tables = dynamodb.meta.client.list_tables()['TableNames']
    if test_table_name in existing_tables:
        table = dynamodb.Table(test_table_name)
        table.delete()
        table.meta.client.get_waiter('table_not_exists').wait(TableName=test_table_name)
    
    table = dynamodb.create_table(
        TableName=test_table_name,
        KeySchema=[
            {'AttributeName': 'EnvironmentName', 'KeyType': 'HASH'},
            {'AttributeName': 'PuppetClusterName', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'EnvironmentName', 'AttributeType': 'S'},
            {'AttributeName': 'PuppetClusterName', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    table.meta.client.get_waiter('table_exists').wait(TableName=test_table_name)
    
    os.environ['DYNAMODB_TABLE_NAME'] = test_table_name

    yield table

    table.delete()
    table.meta.client.get_waiter('table_not_exists').wait(TableName=test_table_name)

@pytest.fixture(scope="function")
def prepare_data(dynamodb):
    dynamodb.scan()['Items'].clear()

def test_create_environment(dynamodb, prepare_data):
    environment_data = {
        "environment_name": "master",
        "puppet_cluster_name": "ny2-saas-n"
    }

    response = client.post("/environment/", json=environment_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert 'message' in data, \
        "Expected 'message' in response, got {}".format(data)
    assert data['message'] == 'Environment created successfully', \
        f"Expected message 'Environment created successfully', got '{data['message']}'"

    result = dynamodb.get_item(Key={
        'EnvironmentName': 'master',
        'PuppetClusterName': 'ny2-saas-n'
    })
    assert 'Item' in result, "Expected item to be present in DynamoDB"

def test_get_environment(dynamodb, prepare_data):
    dynamodb.put_item(Item={
        'EnvironmentName': 'master',
        'PuppetClusterName': 'ny2-saas-n'
    })

    response = client.get("/environment/master/ny2-saas-n")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['EnvironmentName'] == 'master'
    assert data[0]['PuppetClusterName'] == 'ny2-saas-n'

def test_delete_environment(dynamodb, prepare_data):
    dynamodb.put_item(Item={
        'EnvironmentName': 'master',
        'PuppetClusterName': 'ny2-saas-n'
    })

    response = client.delete("/environment/master/ny2-saas-n")
    data = response.json()

    assert response.status_code == 200
    assert data['message'] == 'Environment deleted successfully'

    result = dynamodb.get_item(Key={
        'EnvironmentName': 'master',
        'PuppetClusterName': 'ny2-saas-n'
    })
    assert 'Item' not in result
