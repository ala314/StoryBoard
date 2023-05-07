import os
import boto3
import openai
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)


openai.organization = "org-ONKzPc9RxLgiPwk6DIVhJzlO"
openai.api_key = "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"

defaultRegion = 'us-east-1'
defaultUrl = 'https://polly.us-east-1.amazonaws.com'


def connectToPolly(regionName=defaultRegion, endpointUrl=defaultUrl):
    return boto3.client('polly', region_name=regionName, endpoint_url=endpointUrl)


# def speak(polly, text, format='mp3', voice='Brian'):
#     resp = polly.synthesize_speech(
#         OutputFormat=format, Text=text, VoiceId=voice)
#     soundfile = open('/tmp/sound.mp3', 'w')
#     soundBytes = resp['AudioStream'].read()
#     soundfile.write(soundBytes)
#     soundfile.close()
#     os.system('afplay /tmp/sound.mp3')  # Works only on Mac OS, sorry
#     os.remove('/tmp/sound.mp3')


# polly = connectToPolly()
# speak(polly, "Hello world, I'm Polly. Or Brian. Or anyone you want, really.")


# client = boto3.client('translate', region_name="us-east-1")
# response = client.translate_text(Text=sampText,
#                                  SourceLanguageCode=inpLang,
#                                  TargetLanguageCode=outLang)

# output = response['TranslatedText']

"""
Languege codes

English en 
French	fr
Hindi	hi
Japanese	ja

"""


def lambda_handler(event, context):
    print((event))
    title = event['queryStringParameters']['body']['title']
    story = event['queryStringParameters']['body']['story']
    genre = event['queryStringParameters']['body']['genre']

    print(title, story, genre)

    polly = connectToPolly()

    file_name = title +".mp3"
    resp = polly.synthesize_speech(
        OutputFormat='mp3', Text=story, VoiceId='Brian')
    soundfile = open('/tmp/'+file_name, 'w')
    soundBytes = resp['AudioStream'].read()
    soundfile.write(soundBytes)
    soundfile.close()
    BUCKET_NAME = "storyboard-media-balti"

    lambda_path = "/tmp/" + file_name
    s3_path = file_name
    # os.system('echo testing... >'+lambda_path)
    s3 = boto3.resource("s3")
    s3.meta.client.upload_file(lambda_path, BUCKET_NAME, file_name)


    ########## French ###########
    BUCKET_NAME = "storyboard-story-balti"

    client = boto3.client('translate', region_name="us-east-1")
    response = client.translate_text(Text=story,
                                    SourceLanguageCode='en',
                                    TargetLanguageCode='fr')

    output = response['TranslatedText']
    file_name = title + "_fr.txt"
    s3_path = file_name
    lambda_path = "/tmp/" + file_name
    with open( lambda_path ,'w',encoding='utf8') as f:
        f.write(output)
        
    s3.meta.client.upload_file(lambda_path, BUCKET_NAME, file_name)

    ########## Hindi ###########
    response = client.translate_text(Text=story,
                                    SourceLanguageCode='en',
                                    TargetLanguageCode='hi')

    output = response['TranslatedText']
    file_name = title + "_hi.txt"
    s3_path = file_name
    lambda_path = "/tmp/" + file_name
    with open( lambda_path ,'w',encoding='utf8') as f:
        f.write(output)
        
    s3.meta.client.upload_file(lambda_path, BUCKET_NAME, file_name)

    ########## Japanese ###########
    response = client.translate_text(Text=story,
                                     SourceLanguageCode='en',
                                     TargetLanguageCode='ja')

    output = response['TranslatedText']
    file_name = title + "_ja.txt"
    s3_path = file_name
    lambda_path = "/tmp/" + file_name
    with open( lambda_path ,'w',encoding='utf8') as f:
        f.write(output)
        
    s3.meta.client.upload_file(lambda_path, BUCKET_NAME, file_name)


    ########## English ###########

    file_name = title + "_en.txt"
    s3_path = file_name
    lambda_path = "/tmp/" + file_name
    with open(lambda_path, 'w', encoding='utf8') as f:
        f.write(story)

    s3.meta.client.upload_file(lambda_path, BUCKET_NAME, file_name)

    os.remove("/tmp/"+title+".mp3")
    os.remove("/tmp/"+title+"_en.txt")
    os.remove("/tmp/"+title+"_fr.txt")
    os.remove("/tmp/"+title+"_hi.txt")
    os.remove("/tmp/"+title+"_ja.txt")

    ############ Mood color ##############
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="The CSS code for a color like a blue sky at dusk:\n\nbackground-color: #",
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=[";"]
        )

    mood_color = response['choices'][0]['text']

    ############ Summary ##############
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=story+"\n\ntl;dr:",
        temperature=0,
        max_tokens=64,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=[";"]
    )

    summary = response['choices'][0]['text']

    ############ Word count ##############
    word_ct = len(story.split())


    ############ DynamoDB ##############
    story_data = {"title": title, "summary": summary, "word_ct":word_ct, "genre":genre, "mood_color":mood_color}

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('storyboard_story')

    response = table.put_item(
        Item=story_data
    )


    ############ ElasticSearch ##############
    elastic_data = {'objectKey': title.replace(" ", "_"),
                    'genre': genre}

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

    resp = client.index(index='storyboard', id=title.replace(" ", "_"), body=elastic_data)
    # print(resp)

    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*", "Access-Control-Allow-Headers": "*"},
    }
