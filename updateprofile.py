import os
import boto3


def lambda_handler(event, context):
    print((event))
    user = event['queryStringParameters']['body']['user']
    title = event['queryStringParameters']['body']['title']
    action = event['queryStringParameters']['body']['action']

    if action == "LIKE":
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('stoaryboard_users')
        response = table.get_item(
            Key={
                'user': user
            }
        )
        item = response['Item']
        print(item)
        likes = item['likes']
        likes.append(title)
        table.update_item(
            Key={
                'user': user
            },
            UpdateExpression="set likes = :l",
            ExpressionAttributeValues={
                ':l': likes
            },
            ReturnValues="UPDATED_NEW"
        )
    elif action == "BUY":
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('storyboard_users')
        response = table.get_item(
            Key={
                'user': user
            }
        )
        item = response['Item']
        print(item)
        buys = item['buys']
        buys.append(title)
        table.update_item(
            Key={
                'user': user
            },
            UpdateExpression="set buys = :b",
            ExpressionAttributeValues={
                ':b': buys
            },
            ReturnValues="UPDATED_NEW"
        )
    

    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"},
    }
