#!/usr/bin/env python3

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import datetime
import json
import time
import random
import boto3
import hashlib
import sys

session = boto3.Session(
    # Uncomment to a different AWS Profile than Default
    # profile_name='leah' 
    )
ivs = session.client(
    # Service Name
    'ivs', 
    # Uncomment to use a different AWS Region than Default in Profile
    # region_name='us-west-2',
    )

def get_facts(cat_file="facts.txt"):
    """Returns a list of facts about cats from the cat file (one fact
    per line)"""
    with open(cat_file, "r") as cat_file:
        return [line for line in cat_file]

def put_metadata(channel_arn, metadata_payload):
    """
    Adds metadata to an active stream. 
    There is a limit: at most 5 requests per second per channel 
    are allowed.
    """
    response = ivs.put_metadata(
        channelArn=channel_arn,
        metadata=metadata_payload,
    )
    return response

if __name__ == "__main__":
    if len(sys.argv) > 1:
        channel_arn = sys.argv[1]
        facts = get_facts()
        maybe = ['Maybe', 'Perhaps', 'Feasible', 'Conceivable']
        while True:
            question = random.choice(facts).rstrip()
            data = {
                "current_time" : datetime.datetime.utcnow().strftime('%Y-%b-%d-%H%M%S'),
                "poll_id": str(hashlib.md5(question.encode()).hexdigest()), #create hash for an id for now
                "question": question,
                "answers": {
                    "1": "True",
                    "2": "False",
                    "3": random.choice(maybe).rstrip()
                }
            }
            print(json.dumps(data))
            try:
                response = put_metadata(channel_arn,json.dumps(data))
                print("HTTPStatusCode: {}".format(response['ResponseMetadata']['HTTPStatusCode']))
            except Exception as e: 
                print("ERROR: {}".format(e))
            time.sleep(10)
    else:
        print("please provide IVS ARN\n example: \t ./metadata.py arn:aws:ivs:us-west-2:123456789:channel/abcdEFG123")