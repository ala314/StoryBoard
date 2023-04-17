import os
import boto3
import openai
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import json

openai.organization = "org-ONKzPc9RxLgiPwk6DIVhJzlO"
openai.api_key = "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"

def lambda_handler(event, context):
    print((event))
    user = event['queryStringParameters']['body']['user']
    prompt = event['queryStringParameters']['body']['prompt']

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.3,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    output = response['choices'][0]['text']

    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"},
        'body': json.dumps({"output": output})
    }
