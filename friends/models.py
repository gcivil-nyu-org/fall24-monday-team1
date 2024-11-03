from django.conf import settings
import boto3
from botocore.exceptions import ClientError

class FriendRequest:
    @staticmethod
    def get_dynamodb_resource():
        return boto3.resource(
            'dynamodb',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1'
        )

    @staticmethod
    def get_friend_requests_table():
        dynamodb = FriendRequest.get_dynamodb_resource()
        return dynamodb.Table('friend_requests')

    @staticmethod
    def get_friends_table():
        dynamodb = FriendRequest.get_dynamodb_resource()
        return dynamodb.Table('user_friends')

    @staticmethod
    def send_request(from_user, to_user):
        table = FriendRequest.get_friend_requests_table()
        try:
            table.put_item(
                Item={
                    'to_user': to_user,
                    'from_user': from_user,
                    'status': 'pending'
                }
            )
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    @staticmethod
    def get_pending_requests(user):
        table = FriendRequest.get_friend_requests_table()
        try:
            response = table.query(
                KeyConditionExpression='to_user = :user',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':user': user, ':status': 'pending'}
            )
            return response['Items']
        except ClientError as e:
            print(e.response['Error']['Message'])
            return []

    @staticmethod
    def accept_request(from_user, to_user):
        request_table = FriendRequest.get_friend_requests_table()
        friends_table = FriendRequest.get_friends_table()
        try:
            # Update request status
            request_table.update_item(
                Key={'to_user': to_user, 'from_user': from_user},
                UpdateExpression='SET #status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': 'accepted'}
            )
            # Add to friends list for both users
            friends_table.put_item(Item={'user': to_user, 'friend': from_user})
            friends_table.put_item(Item={'user': from_user, 'friend': to_user})
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    @staticmethod
    def reject_request(from_user, to_user):
        table = FriendRequest.get_friend_requests_table()
        try:
            table.delete_item(Key={'to_user': to_user, 'from_user': from_user})
            return True
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False

    @staticmethod
    def get_friends(user):
        table = FriendRequest.get_friends_table()
        try:
            response = table.query(
                KeyConditionExpression='user = :user',
                ExpressionAttributeValues={':user': user}
            )
            return [item['friend'] for item in response['Items']]
        except ClientError as e:
            print(e.response['Error']['Message'])
            return []
        

    @staticmethod
    def get_sent_requests(user):
        table = FriendRequest.get_friend_requests_table()
        try:
            response = table.query(
                IndexName='from_user-index',
                KeyConditionExpression='from_user = :user',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':user': user, ':status': 'pending'}
            )
            return response['Items']
        except ClientError as e:
            print(e.response['Error']['Message'])
            return []