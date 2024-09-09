# lambdas/src/handlers/node.py
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
import boto3
import os
from mangum import Mangum
from boto3.dynamodb.conditions import Key

# Initialize FastAPI app
app = FastAPI()

# Use the table name from the environment variable or default to 'Node'
table_name = os.getenv('DYNAMODB_TABLE_NAME', 'Node')

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
node_table = dynamodb.Table(table_name)

# Health check endpoint
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

# Define Pydantic model for Node
class Node(BaseModel):
    unique_name: str
    node_group_name: str
    environment_name: str
    puppet_cluster_name: str

@app.post("/nodes/")
async def create_node(node: Node):
    response = node_table.query(
        KeyConditionExpression=Key('UniqueName').eq(node.unique_name)
    )
    if response['Items']:
        raise HTTPException(status_code=400, detail="Node with this UniqueName already exists")
    
    item = {
        "UniqueName": node.unique_name,
        "NodeGroupName": node.node_group_name,
        "environment_name": node.environment_name,
        "puppet_cluster_name": node.puppet_cluster_name,
    }
    
    node_table.put_item(Item=item)
    return {"message": "Node created successfully"}

@app.get("/nodes/{unique_name}")
async def read_node(unique_name: str = Path(..., description="The unique name of the node to retrieve")):
    response = node_table.query(
        KeyConditionExpression=Key('UniqueName').eq(unique_name)
    )
    items = response.get('Items', [])
    if not items:
        raise HTTPException(status_code=404, detail="Node not found")
    return items

@app.put("/nodes/{unique_name}")
async def update_node(unique_name: str, node: Node):
    response = node_table.query(
        KeyConditionExpression=Key('UniqueName').eq(unique_name)
    )
    items = response.get('Items', [])
    if not items:
        raise HTTPException(status_code=404, detail="Node not found")
    
    existing_item = items[0]
    node_table.delete_item(Key={
        'UniqueName': existing_item['UniqueName'],
        'NodeGroupName': existing_item['NodeGroupName']
    })
    node_table.put_item(Item={
        "UniqueName": node.unique_name,
        "NodeGroupName": node.node_group_name,
        "environment_name": node.environment_name,
        "puppet_cluster_name": node.puppet_cluster_name,
    })
    return {"message": "Node updated successfully"}

@app.delete("/nodes/{unique_name}")
async def delete_node(unique_name: str):
    response = node_table.query(
        KeyConditionExpression=Key('UniqueName').eq(unique_name)
    )
    items = response.get('Items', [])
    if not items:
        raise HTTPException(status_code=404, detail="Node not found")
    
    item = items[0]
    node_table.delete_item(
        Key={'UniqueName': item['UniqueName'], 'NodeGroupName': item['NodeGroupName']}
    )
    return {"message": "Node deleted successfully"}

# @app.get("/nodes/")
# async def get_all_nodes():
#     response = node_table.scan()
#     items = response.get('Items', [])
#     return items

# @app.get("/nodes/puppet_cluster/{puppet_cluster_name}")
# async def get_nodes_by_puppet_cluster(puppet_cluster_name: str):
#     response = node_table.query(
#         IndexName="PuppetClusterIndex",  # Assuming there is a secondary index for PuppetClusterName
#         KeyConditionExpression=Key('PuppetClusterName').eq(puppet_cluster_name)
#     )
#     items = response.get('Items', [])
#     if not items:
#         raise HTTPException(status_code=404, detail="No nodes found for this Puppet Cluster")
#     return items

# @app.get("/nodes/hostgroup/{node_group_name}")
# async def get_nodes_by_hostgroup(node_group_name: str):
#     response = node_table.query(
#         IndexName="NodeGroupNameIndex",  # Assuming there is a secondary index for NodeGroupName
#         KeyConditionExpression=Key('NodeGroupName').eq(node_group_name)
#     )
#     items = response.get('Items', [])
#     if not items:
#         raise HTTPException(status_code=404, detail="No nodes found for this Hostgroup")
#     return items

# @app.get("/nodes/environment/{environment_name}")
# async def get_nodes_by_environment(environment_name: str):
#     response = node_table.query(
#         IndexName="EnvironmentIndex",  # Assuming there is a secondary index for EnvironmentName
#         KeyConditionExpression=Key('EnvironmentName').eq(environment_name)
#     )
#     items = response.get('Items', [])
#     if not items:
#         raise HTTPException(status_code=404, detail="No nodes found for this Environment")
#     return items


#  Mangum handler to run FastAPI app on AWS Lambda
handler = Mangum(app)

