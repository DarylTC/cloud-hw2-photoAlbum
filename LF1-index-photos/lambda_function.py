import boto3
import json
import base64
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch
import time
from requests_aws4auth import AWS4Auth
import requests

def lambda_handler(event, context):
    print(event)
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    photo = event['Records'][0]['s3']['object']['key']
    # eventTime = event['Records'][0]['eventTime']

    timestamp = time.gmtime()
    time_created = time.strftime("%Y-%m-%dT%H:%M:%S", timestamp)

    print('bucket: ', bucket)
    print('photo: ', photo)
    
    # de code img
    s3obj = boto3.client('s3')
    getobj=s3obj.get_object(Bucket=bucket,Key=photo)
    body=getobj['Body'].read().decode('utf-8')
    imagebase64 = base64.b64decode(body)
    
    headobj=s3obj.head_object(Bucket=bucket,Key=photo)    
    #
    
    client=boto3.client('rekognition','us-east-1')
    # response = client.detect_labels(
    #     Image={'S3Object':
    #             {'Bucket':bucket,
    #             'Name':photo
    #             }
    #         },
    #     MaxLabels=10, MinConfidence=80)
    
    response = client.detect_labels(
        Image={'Bytes': imagebase64},
        MaxLabels=10, MinConfidence=80)
        
    label_list = []
    for label in response['Labels']:
        label_list.append(label['Name'])
        
    print(label_list)
    
    # S3 metadata
    s3_client = boto3.client('s3')
    s3_head_object = s3_client.head_object(
        Bucket=bucket,
        Key=photo
    )
    print(s3_head_object['ResponseMetadata']['HTTPHeaders'])
    custom_labels = []
    meta_custom_label = 'x-amz-meta-customlabels' #the metadata field wanted (if exist)
    if (meta_custom_label in s3_head_object['ResponseMetadata']['HTTPHeaders']):
        custom_labels.append(s3_head_object['ResponseMetadata']['HTTPHeaders'][meta_custom_label])
        print(custom_labels)

    
    #json object to elastic search (need to json.dumps() later)
    obj_to_elastic_search = {
        'objectKey': photo,
        'bucket': bucket,
        'createdTimestamp': time_created,
        'labels': label_list + custom_labels
    }

    print("Json object: ", json.dumps(obj_to_elastic_search))

    # send to elastic search...
    es_domain_endpoint = 'https://search-photos-hfyhtujlb2vm2br555f4czljly.us-east-1.es.amazonaws.com'
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    essearch=es_domain_endpoint+'/'+'photos'+'/'+'_doc'
    req = requests.post(essearch,auth=awsauth, headers = { "Content-Type": "application/json" }, data=json.dumps(obj_to_elastic_search))
   
    print(req)
   
    return {
        'statusCode': 200,
        'body': json.dumps('Done indexing to ES')
    }
