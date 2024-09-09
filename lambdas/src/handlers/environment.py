# lambdas/src/handlers/environment.py
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
import boto3
import os
from mangum import Mangum
from boto3.dynamodb.conditions import Key

app = FastAPI()

# Use the table name from the environment variable or default to 'Environment'
table_name = os.getenv('DYNAMODB_TABLE_NAME', 'Environment')

dynamodb = boto3.resource('dynamodb')
environment_table = dynamodb.Table(table_name)

# Health check endpoint
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

# Define Pydantic model for Environment
class Environment(BaseModel):
    environment_name: str
    puppet_cluster_name: str

@app.post("/environment/")
async def create_environment(environment: Environment):
    item = {
        'EnvironmentName': environment.environment_name,
        'PuppetClusterName': environment.puppet_cluster_name,
    }
    environment_table.put_item(Item=item)
    return {"message": "Environment created successfully"}

@app.get("/environment/{environment_name}/{puppet_cluster_name}")
async def read_environment(environment_name: str, puppet_cluster_name: str):
    response = environment_table.query(
        KeyConditionExpression=Key('EnvironmentName').eq(environment_name) & Key('PuppetClusterName').eq(puppet_cluster_name)
    )
    items = response.get('Items', [])
    if not items:
        raise HTTPException(status_code=404, detail="Environment not found")
    return items

@app.delete("/environment/{environment_name}/{puppet_cluster_name}")
async def delete_environment(environment_name: str, puppet_cluster_name: str):
    environment_table.delete_item(
        Key={'EnvironmentName': environment_name, 'PuppetClusterName': puppet_cluster_name}
    )
    return {"message": "Environment deleted successfully"}

handler = Mangum(app)

