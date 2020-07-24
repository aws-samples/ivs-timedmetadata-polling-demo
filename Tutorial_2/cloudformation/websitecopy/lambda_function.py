from crhelper import CfnResource
import tempfile, os
import boto3
import json
import requests, zipfile, io

helper = CfnResource()

@helper.create
@helper.update
def sum_2_numbers(event, _):
    helper.Data['BucketName'] = event['ResourceProperties']['BucketName']
    bucket_name = event['ResourceProperties']['BucketName']
    client = boto3.client("s3")
    with tempfile.TemporaryDirectory() as tmpdirname:
        print('created temporary directory', tmpdirname)
        dictionary = {
            'bucket_name': event['ResourceProperties']['BucketName'],
            'playback_url': event['ResourceProperties']['PlaybackUrl'],
            'api_gateway': event['ResourceProperties']['ApiGateway'],
            
        }
        # Writing to sample.json 
        json_object = json.dumps(dictionary, indent = 4)
        remote = 'sample.json'
        local = tmpdirname + "/" + remote
        content_type = "binary/octet-stream"
        with open(local, "w") as outfile: 
            outfile.write(json_object) 
        client.put_object(Bucket=bucket_name, Key=remote, Body=open(local, 'rb'), ContentType=content_type)
        # GET zip file
        website_bucket = event['ResourceProperties']['WebsiteS3Bucket']
        website_key = event['ResourceProperties']['WebsiteS3Key']
        # TODO hardcoded region removal
        zip_file_url = "https://{website_bucket}.s3.us-east-1.amazonaws.com/{website_key}".format(website_bucket=website_bucket, website_key=website_key)
        r = requests.get(zip_file_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(tmpdirname)
        for dirpath, _, filenames in os.walk(tmpdirname):
            for name in filenames:
                local = "{}/{}".format(dirpath, name)
                remote = local.replace("{}/".format(tmpdirname), "")
                content_type = None
                if remote.endswith(".js"):
                    content_type = "application/javascript"
                elif remote.endswith(".html"):
                    content_type = "text/html"
                elif remote.endswith(".css"):
                    content_type = "text/css"
                else:
                    content_type = "binary/octet-stream"
                client.put_object(Bucket=bucket_name, Key=remote, Body=open(local, 'rb'), ContentType=content_type)
    # directory and contents have been removed


def delete_bucket_contents(bucket_name):
    """
    This function is responsible for removing all contents from the specified bucket.
    """
    client = boto3.client("s3")
    response = client.list_objects_v2(Bucket=bucket_name)
    if "Contents" in response:
        for item in response["Contents"]:
            client.delete_object(Bucket=bucket_name, Key=item["Key"])

@helper.delete
def delete(event, context):
    print(event)
    bucket_name = event['ResourceProperties']['BucketName']
    delete_bucket_contents(bucket_name)

def handler(event, context):
    helper(event, context)