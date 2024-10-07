import requests
import boto3
import json


sagemaker_client = boto3.client('runtime.sagemaker')


LLAMA3_LOCAL_ENDPOINT = "http://localhost:5000/generate-summary"
SAGEMAKER_ENDPOINT_NAME = 'llama3-endpoint'

def generate_summary_with_llama3(book_content):
    response = requests.post(LLAMA3_LOCAL_ENDPOINT, json={"text": book_content})
    return response.json().get("summary")

def generate_summary_with_sagemaker(book_content):
    response = sagemaker_client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT_NAME,
        ContentType='application/json',
        Body=json.dumps({"text": book_content})
    )
    result = json.loads(response['Body'].read().decode())
    return result.get("summary")
