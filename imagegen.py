import os

import openai
import requests
import matplotlib.pyplot as plt
from base64 import b64decode


# PROMPT = "A bustling New York street"

openai.organization = "org-ONKzPc9RxLgiPwk6DIVhJzlO"
openai.api_key = "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"

# response = openai.Image.create(
#     prompt=PROMPT,
#     n=1,
#     size="256x256",
#     response_format="b64_json",
# )

# print(response["data"][0]["url"])

# img_data = requests.get(response["data"][0]["url"]).content
# with open('dalle.png', 'wb') as handler:
#     handler.write(img_data)

# print(img_data)

# print(response["data"][0]["b64_json"])

# img_data = b64decode(response["data"][0]["b64_json"])
# with open('dalle.png', 'wb') as handler:
#     handler.write(img_data)

# print(img_data)


def lambda_handler(event, context):
    print((event))
    title = event['queryStringParameters']['body']['title']
    prompt = event['queryStringParameters']['body']['prompt']

    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="256x256",
        response_format="b64_json",
    )
    print(response["data"][0]["b64_json"])

    file_name = title+'.png'
    lambda_path = "/tmp/" + file_name
    img_data = b64decode(response["data"][0]["b64_json"])
    with open(lambda_path, 'wb') as handler:
        handler.write(img_data)
    
    BUCKET_NAME = "storyboard-media-balti"
    s3 = boto3.resource("s3")
    s3.meta.client.upload_file(lambda_path, BUCKET_NAME, file_name)

    os.remove("/tmp/"+file_name)
    # print(img_data)

    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"},
    }
