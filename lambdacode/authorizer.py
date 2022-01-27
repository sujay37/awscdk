import json
import os
import logging
import requests
import jwt

import sys

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
format = logging.Formatter("%(levelname)s - %(message)s")

console = logging.StreamHandler(sys.stdout)
console.setFormatter(format)
logger.addHandler(console)

def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def verify_token(token):
    """Make an API request to User APIs"""
    x_api_key = os.environ.get('api_key', '')
    COGNITO_API = os.environ.get('cognito_api', '')
    headers = {
        'x-api-key': x_api_key,
        'Content-Type': 'application/json',
        'Accept' : 'application/json'
    }

    cognito_api_url = COGNITO_API + '/user/verify-token'
    payload = { "token": token }
    logger.info("Verifying the API token ...")

    response = requests.post(cognito_api_url, headers=headers, data=json.dumps(payload).encode('utf8'), verify=True)
    if response.status_code == 200:
        logger.info("Token verification completed")
        if response.text:
            response_json = json.loads(response.text)
            logger.info("Response : " +  response.text);
            return response_json["success"]
    else:
        logger.error("Failed to verify token");
        return False

def generatePolicy(principalId, effect, methodArn):
    authResponse = {}
    authResponse['principalId'] = principalId

    if effect and methodArn:
        policyDocument = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'Stmt01',
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': methodArn
                }
            ]
        }

        authResponse['policyDocument'] = policyDocument

    return authResponse


def lambda_handler(event, context):
    logger.info("Received token for verification")
    try:
        logger.info("Validating and decoding token")
        #Remove the Bearer prefix
        auth_token = remove_prefix(event['authorizationToken'], 'Bearer ')
        decoded_token = jwt.decode(auth_token, options={"verify_signature": False})
        # Get principalId from token
        principalId = decoded_token['sub']

        # Verify id_token received from the client
        isTokenVerified = verify_token(auth_token)
        logger.info("Token valid : {} ".format(isTokenVerified))
        if isTokenVerified:
            logger.info("API Access granted for user : {} ".format(principalId))
            return generatePolicy(principalId, 'Allow', event['methodArn'])
        else:
            # Deny access if the token is invalid
            logger.error("API Access denied for user : {} ".format(principalId))
            return generatePolicy(None, 'Deny', event['methodArn'])

    except:
        # Deny access if the token is incorrect
        logger.error("Token decoding failed")
        return generatePolicy(None, 'Deny', event['methodArn'])

