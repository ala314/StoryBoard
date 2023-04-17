import json
import boto3
# import requests
# from botocore.vendored import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import seaborn
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator





def lambda_handler(event, context):
    print((event))
    user = event['queryStringParameters']['body']['user']

    s3 = boto3.client('s3')
    
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

    genres = []
    word_ct = 0
    text = ""
    table = dynamodb.Table('storyboard_story')
    for buy in buys:
        response = table.get_item(
            Key={
                'title': buy
            }
        )
        item = response['Item']
        genres.append(item['genre'])
        word_ct += len(item['word_ct'])
        obj = client.get_object(Bucket='storyboard-story-balti', Key=item['title']+"_en.txt")
        file=open(obj,"r")
        text += file.read()
        file.close()
    

    
    wordcloud = WordCloud(stopwords=STOPWORDS,
                          background_color="white").generate(text)

    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()




    print(results)
    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"},
        'body': json.dumps({"files": list(results)})
    }
