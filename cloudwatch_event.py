#https://minalogs.com/notify-slack-start-end-codebuild/

import boto3
import json
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    logger.info("Event: " + str(event))
    
    if 'detail' in event:
        project = event["detail"]["project-name"]
        state = event["detail"]["build-status"]

        slack_message = {
            'channel': SLACK_CHANNEL,
            'text': "CodeBuild: %s - %s" % (project, state)
        }

        req = Request(SLACK_WEBHOOK_URL, json.dumps(slack_message).encode('utf-8'))

        try:
            response = urlopen(req)
            response.read()
            logger.info("Message posted to %s", slack_message['channel'])
        except HTTPError as e:
            logger.error("Request failed: %d %s", e.code, e.reason)
        except URLError as e:
            logger.error("Server connection failed: %s", e.reason)
    pipeline = boto3.client('codepipeline')

    job_id = event['CodePipeline.job']['id']
    return pipeline.put_job_success_result(jobId=job_id)