import os
import json
import boto3
import dotenv

REGION = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-1")
FunctionName = os.getenv(
    "FUNC_NAME", "movielens1m-transformer-based-recommender-lambda")
dotenv.load_dotenv("./../.env")

session = boto3.Session(region_name=REGION)

lambda_client = session.client('lambda')

with open("./integration_test/test_healthcheck_payload.json", mode='r', encoding='utf-8') as f:
    payload = f.read()

response = lambda_client.invoke(
    FunctionName=FunctionName,
    Payload=payload
)

response = json.loads(response['Payload'].read().decode('utf-8'))

print(response)

assert response['statusCode'] == 200

with open("./integration_test/test_recommend_payload.json", mode='r', encoding='utf-8') as f:
    payload = f.read()

response = lambda_client.invoke(
    FunctionName=FunctionName,
    Payload=payload
)

response = json.loads(response['Payload'].read().decode('utf-8'))

print(response)

assert response['statusCode'] == 200
