from operator import and_
import boto3
import json
import base64
from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch
import time
from requests_aws4auth import AWS4Auth
import requests

def lambda_handler(event, context):
    
    test_body_message = 'show me the photos with trees and birds in them'
    
    # Lex
    lex_client = boto3.client('lex-runtime')
    response = lex_client.post_text(
      botName='Search_Photos',
      botAlias='dev',
      userId='cloud',
      inputText=test_body_message
    )
    
    keyword_one = response['slots']['keywordOne']
    keyword_two = response['slots']['keywordTwo']
    print(keyword_one,keyword_two)
    
    # Elastic search
    region = 'us-east-1'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    host = 'https://search-photos-hfyhtujlb2vm2br555f4czljly.us-east-1.es.amazonaws.com' # The OpenSearch domain endpoint with https://
    index = 'photos'
    url = host + '/' + index + '/_search'
    
    # Put the user query into the query DSL for more accurate search results.
    # query = {
    #     "size": 5,
    #     "query": {
    #         "multi_match": {
    #             "query": "tree",
    #             "fields": ["labels"]
    #         }
    #     }
    # }

    # pre-processing to get rid of s
    if (keyword_one.lower() == 'trees'):
        keyword_one = 'tree'
    if (keyword_one.lower() == 'birds'):
        keyword_one = 'bird'
    if (keyword_two is not None and keyword_two.lower() == 'trees'):
        keyword_two = 'tree'
    if (keyword_two is not None and keyword_two.lower() == 'birds'):
        keyword_two = 'bird'

    if (keyword_two is not None):
        query_str = "(%s) OR (%s)"%(keyword_one,keyword_two)
    else:
        query_str = "(%s)"%(keyword_one)

    # query setup
    query = {
        "query": {
            "query_string": {
              "query": query_str,
              "default_field": "labels",
              "fuzziness": "AUTO",
              "fuzzy_prefix_length": "4"
            }
        }    
    }
    
    # Elasticsearch 6.x requires an explicit Content-Type header
    headers = { "Content-Type": "application/json" }

    # Make the signed HTTP request
    r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))
    results = json.loads(r.text)
    resultContent = results['hits']['hits']
    photo_List = []
    for res in resultContent:
        photo_name = res['_source']['objectKey']
        if photo_name not in photo_List:
            photo_List.append(photo_name)
    
    result = {
        'photoPath': photo_List
    }
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(result)
    }
