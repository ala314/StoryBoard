import os
import boto3


def lambda_handler(event, context):
    print((event))
    user = event['queryStringParameters']['body']['user']
    searchquery = event['queryStringParameters']['q']

    if searchquery=="recommend":
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('storyboard_users')
        response = table.get_item(
            Key={
                'user': user
            }
        )
        item = response['Item']
        return {
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"},
            'body': json.dumps({"files": item['recommend']})
        }
    else:

        REGION = 'us-east-1'
        HOST = "story-board-tyo2a2wcxqrw4ntex5gzhk5oya.us-east-1.es.amazonaws.com"  # add host here
        INDEX = "storyboard"  # add index
        client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
        }],
        http_auth=get_awsauth(REGION, 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)

        results = set()
        for k in keys:
            q = {'size': 100, 'query': {'multi_match': {'query': k}}}
            res = client.search(index=INDEX, body=q)
            hits = res['hits']['hits']
            for hit in hits:
                results.add(hit['_source']['objectKey'].replace("_", " "))

        print(results)

        return {
            'statusCode': 200,
            'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"},
            'body': json.dumps({"files": list(results)})
        }
