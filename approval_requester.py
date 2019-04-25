# This function is invoked via SNS when the CodePipeline manual approval action starts.
# It will take the details from this approval notification and sent an interactive message to Slack that allows users to approve or cancel the deployment.

import os
import json
import logging
import urllib.parse

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# This is passed as a plain-text environment variable for ease of demonstration.
# Consider encrypting the value with KMS or use an encrypted parameter in Parameter Store for production deployments.
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']
STAGE_NAME = os.environ['STAGE_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    message = event["Records"][0]["Sns"]["Message"]
    
    data = json.loads(message) 
    token = data["approval"]["token"]
    externalEntityLink = data["approval"]["externalEntityLink"]
    approvalReviewLink = data["approval"]["approvalReviewLink"]
    customData = data["approval"]["customData"]
    codepipeline_name = data["approval"]["pipelineName"]
    
    slack_message = {
        "channel": SLACK_CHANNEL,
        "text": "Deployment to _%s_ environment is a success" % (STAGE_NAME),
        "attachments": [
            {
                "text": "App: *%s* (Link: %s)\n<%s|Review the CodePipeline Execution>\nWould you like to promote the build to production? :rocket:" % (codepipeline_name, externalEntityLink, approvalReviewLink),
                "fallback": "You are unable to promote a build",
                "callback_id": "wopr_game",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "deployment",
                        "text": "Yes",
                        "style": "danger",
                        "type": "button",
                        "value": json.dumps({"approve": True, "codePipelineToken": token, "codePipelineName": codepipeline_name}),
                        "confirm": {
                            "title": "Confirm",
                            "text": "Are you sure you want to promote to production?",
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    },
                    {
                        "name": "deployment",
                        "text": "No",
                        "type": "button",
                        "value": json.dumps({"approve": False, "codePipelineToken": token, "codePipelineName": codepipeline_name})
                    }  
                ]
            }
        ]
    }

    req = Request(SLACK_WEBHOOK_URL, json.dumps(slack_message).encode('utf-8'))

    response = urlopen(req)
    response.read()
    
    return None