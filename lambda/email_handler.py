import json
import boto3
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Function to retrieve email from DynamoDB
def get_email_from_dynamodb(api_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('EmailApiKeyTable')

    try:
        response = table.get_item(Key={'apiKey': api_key})
        email = response.get('Item', {}).get('email')
        return email
    except ClientError as error:
        print(f"Error retrieving email from DynamoDB: {error}")
        return None

# Function to send email using SES
def send_email(sender_email, recipient_email, subject, body):
    ses = boto3.client('ses')

    charset = "UTF-8"

    try:
        response = ses.send_email(
            Destination={
                'ToAddresses': [
                    recipient_email,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': charset,
                        'Data': body,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender_email,
        )
        print(f"Email sent successfully. Message ID: {response['MessageId']}")
    except ClientError as error:
        print(f"Error sending email: {error}")

# Lambda handler function
def lambda_handler(event, context):
    try:
        api_key = event['params']['header']['x-api-key']
        sender_email = event['body-json']['email']
        message_body = event['body-json']['message']
        subject = "Portfolio Contact Form Submission"
        
        # Retrieve email from DynamoDB
        recipient_email = get_email_from_dynamodb(api_key)

        logger.info(f"Emails {sender_email}, {recipient_email}")
        if not recipient_email:
            raise Exception("Failed to retrieve recipient email")

        # Send email notification
        send_email(sender_email, recipient_email, subject, message_body)

        return {
            'statusCode': 200,
            'body': json.dumps('Email notification sent successfully!')
        }

    except Exception as error:
        print(f"Error processing request: {error}")
        return {
            'statusCode': 500,
            # 'body': json.dumps('An error occurred while processing your request.')
            'body': f'An error occurred while processing your request: {error}'
        }
