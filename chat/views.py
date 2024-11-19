from django.shortcuts import render, redirect
import boto3
import os
from checkpoint.settings import ENV

from boto3.dynamodb.conditions import Attr


def chatPage(request, to, room_id):
    if not request.user.is_authenticated:
        return redirect("login")
    # TODO: check if from and to already have a chat UUID on Dynamo, if yes use that, so that the two users can connect to the same UUID
    # if not, add this UUID to the table

    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    # Reference the DynamoDB table
    if ENV=="PROD":
        table = dynamodb.Table('chatrooms')
    elif not ENV or ENV=="DEV":
        table = dynamodb.Table('dev-chatrooms')    

    filter_expression = (Attr('from').eq(request.user.username) & Attr('to').eq(to)) | (Attr('to').eq(request.user.username) & Attr('from').eq(to))
    scan_params = {
    'FilterExpression': filter_expression,
    }
    response = table.scan(**scan_params)
    if response['Items']:
        room_id = response['Items'][0]['room_uuid']
        print("existing room, fetch history pending")
    else:
        # add this to the table
        table.put_item(Item={
            'room_uuid': room_id,
            'from': request.user.username,
            'to':to
        })
        print("created new room")
      

    context = {
        "room_name": room_id,
    }
    return render(request, "chat/chatPage.html", context)