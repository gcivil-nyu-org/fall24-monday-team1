
import boto3
import os
from botocore.exceptions import ClientError
from checkpoint.settings import ENV
import uuid


class ChatMessage:
    def __init__(self, room_uuid, sender, receiver, timestamp, content):
        self.msgid = str(uuid.uuid4())
        self.msg = content
        self.room_uuid = room_uuid
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp
    
    def save(self):
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )
        if ENV=="PROD":
            table = dynamodb.Table('chathistory')
        elif not ENV or ENV=="DEV":
            table = dynamodb.Table('dev-chathistory')   
        print(table)
        item = self.__dict__.copy()
        item['timestamp'] = str(item['timestamp'])
        try:
            table.put_item(Item=item)
        except Exception as e:
            print(e)
        


