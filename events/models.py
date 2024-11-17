import boto3
import os
import uuid
from botocore.exceptions import ClientError

class Event:
    def __init__(self, title, description, start_time, end_time, location, creator, participants=None, event_id=None):
        self.eventId = event_id or str(uuid.uuid4())  # Use provided event_id or generate a new one
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.location = location
        self.creator = creator
        self.participants = set(participants) if participants is not None else set()  # Initialize participants as a set

    def add_participant(self, participant):
        """Add a participant to the event."""
        self.participants.add(participant)  # Sets automatically handle duplicates
        
    def remove_participant(self, participant):
        """Remove a participant from the event."""
        self.participants.discard(participant)  # Use discard to avoid KeyError if not present

    def toggle_participant(self, participant):
        """Toggle a participant's attendance at the event."""
        if participant in self.participants:
            self.remove_participant(participant)
        else:
            self.add_participant(participant)
            
    def save(self):
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            region_name='us-east-1'
        )
        # Convert the set of participants to a list for storage
        item = self.__dict__.copy()
        item['participants'] = list(self.participants)  # Convert set to list for DynamoDB
        table = dynamodb.Table('Events')  # Replace with your DynamoDB table name
        try:
            table.put_item(Item=item)
        except ClientError as e:
            print("Error saving event:", e.response['Error']['Message'])