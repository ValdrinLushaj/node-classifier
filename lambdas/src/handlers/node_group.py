# lambdas/src/handlers/node_group.py
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
import boto3
import json
import os
from mangum import Mangum
from boto3.dynamodb.conditions import Key

# Initialize FastAPI app
app = FastAPI()

# Use the table name from the environment variable or default to 'NodeGroup'
table_name = os.getenv('DYNAMODB_TABLE_NAME', 'NodeGroup')

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
node_group_table = dynamodb.Table(table_name)

# Define Pydantic model for NodeGroup
class NodeGroup(BaseModel):
    name: str
    class_: str  # 'class' is a reserved keyword in Python, using 'class_' instead
    parameters: dict
    
# Health check endpoint
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

@app.post("/nodegroup/")
async def create_node_group(node_group: NodeGroup):
    response = node_group_table.query(
        KeyConditionExpression=Key('Name').eq(node_group.name)
    )
    if response['Items']:
        raise HTTPException(status_code=400, detail="Node group with this name already exists")
    
    node_group_table.put_item(Item={
        "Name": node_group.name,
        "Class": node_group.class_,
        "Parameters": json.dumps(node_group.parameters)
    })
    return {"message": "Node Group created successfully"}

@app.get("/nodegroup/{node_group_name}")
async def read_node_group(node_group_name: str = Path(..., description="The name of the node group to retrieve")):
    response = node_group_table.query(
        KeyConditionExpression=Key('Name').eq(node_group_name)
    )
    items = response.get('Items', [])
    if not items:
        raise HTTPException(status_code=404, detail="Node group not found")
    return items

@app.put("/nodegroup/{node_group_name}")
async def update_node_group(node_group_name: str, node_group: NodeGroup):
    response = node_group_table.query(
        KeyConditionExpression=Key('Name').eq(node_group_name)
    )
    items = response.get('Items', [])
    if not items:
        raise HTTPException(status_code=404, detail="Node group not found")
    
    existing_item = items[0]
    node_group_table.delete_item(Key={
        'Name': existing_item['Name'],
        'Class': existing_item['Class']
    })
    node_group_table.put_item(Item={
        "Name": node_group_name,
        "Class": node_group.class_,
        "Parameters": json.dumps(node_group.parameters)
    })
    return {"message": "Node Group updated successfully"}

@app.delete("/nodegroup/{node_group_name}")
async def delete_node_group(node_group_name: str):
    response = node_group_table.query(
        KeyConditionExpression=Key('Name').eq(node_group_name)
    )
    items = response.get('Items', [])
    if not items:
        raise HTTPException(status_code=404, detail="Node group not found")
    
    item = items[0]
    node_group_table.delete_item(
        Key={'Name': item['Name'], 'Class': item['Class']}
    )
    return {"message": "Node group deleted successfully"}

handler = Mangum(app)

