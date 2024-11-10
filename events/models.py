import boto3
import os
import uuid
from botocore.exceptions import ClientError

class Event:
    def __init__(self, title, description, start_time, end_time, location, creator):
        self.eventId = str(uuid.uuid4())  # Generate a unique event ID
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.creator = creator

    def save(self):
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )
        table = dynamodb.Table('Events')  # Replace with your DynamoDB table name
        try:
            table.put_item(Item=self.__dict__)
        except ClientError as e:
            print("Error saving event:", e.response['Error']['Message'])