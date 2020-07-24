#!/usr/bin/env python

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from botocore.client import Config
import uuid
import json
from pprint import pprint
import time
import os

# DYNAMO Global Vars
DYNAMO_CONFIG = Config(connect_timeout=0.250, read_timeout=0.250, retries={'max_attempts': 1})
DYNAMO_RESOURCE = boto3.resource('dynamodb', config=DYNAMO_CONFIG)
DYNAMO_TABLE_NAME = 'not-set'
DYNAMO_INDEX = "requestor_id-timestamp_created-index"

DEBUG_LEVEL = "INFO"

def write_log(log_level, log_string):
    log_label = {
        "OFF"   : 0,
        "ERROR" : 1,
        "WARN"  : 2,
        "INFO"  : 3,
    }
    if log_label[log_level] <= log_label[DEBUG_LEVEL]:
        print("{}: {}".format(log_level,log_string))
def lambda_handler(event, context):
    DYNAMO_TABLE_NAME = os.getenv('DYNAMO_TABLE_NAME', 'not-set')
    write_log("INFO", "event: {}".format(json.dumps(event)))
    status_code = 500
    message = {
        'state': 'fail'
    }
    if DYNAMO_TABLE_NAME == 'not-set':
        write_log("ERROR", "Environment Variable DYNAMO_TABLE_NAME is not set")
        status_code = 200
        message['state'] = 'broke'
    ## PUT - the requestor's response to the pol
    elif event['path'] == '/requestor-put':
        try:
            if 'body' in event:
                response = json.loads(event['body'])
                if 'type' in response: 
                    if response['type'] == 'answer': 
                        table = DYNAMO_RESOURCE.Table(DYNAMO_TABLE_NAME)
                        item = {
                            "requestor_id": str(response['requestor_id']),
                            "poll_id": str(response['poll_id']),
                            "type": str(response['type']), 
                            "response": str(response['response']),
                            "timestamp_created": int(time.time()),
                            "timestamp_ttl": int(time.time()) + 3600 # 1hr
                            }
                        d_response = table.put_item(Item=item)
                        write_log("INFO", "DynamoDB Succesful: {}".format(d_response))
                        status_code = 200
                        message['state'] = 'success'
                else:
                    write_log("WARNING", "type does not exist in response, doing nothing")
        except:
            status_code = 200
            message['state'] = 'broke'

    ## GET - the requestor's answers
    elif event['path'] == '/requestor-get':
        response = json.loads(event['body'])
        requestor_id = response['requestor_id']
        table = DYNAMO_RESOURCE.Table(DYNAMO_TABLE_NAME)
        d_response = table.query(
            KeyConditionExpression=Key('requestor_id').eq(requestor_id),
            ScanIndexForward=False,
            Limit=5,
            IndexName=DYNAMO_INDEX,
        )
        pprint(d_response['Items'])
        message['items'] = {}
        for item in d_response['Items']:
            message['items'][item['poll_id']] = item['response']
        status_code = 200
        message['state'] = 'success'

    ## GET - the poll's answers
    elif event['path'] == '/poll-get':
        response = json.loads(event['body'])
        poll_id = response['poll_id']
        table = DYNAMO_RESOURCE.Table(DYNAMO_TABLE_NAME)
        d_response = table.query(
            KeyConditionExpression=Key('poll_id').eq(poll_id),
            ScanIndexForward=False,
        )
        pprint(d_response['Items'])
        message['items'] = {}
        responses = {}
        for item in d_response['Items']:
            message['items'][item['requestor_id']] = item['response']
            if item['response'] not in responses:
                responses[item['response']] = 0
            responses[item['response']] = responses[item['response']] + 1
        message['responses'] = responses
        status_code = 200
        message['state'] = 'success'

    ## If not path matches
    else:
        write_log("ERROR", "invalid path: {}".format(event['path']))

    ## Response to webpage
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            },
        }
