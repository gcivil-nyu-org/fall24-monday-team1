from django.shortcuts import render, redirect
import boto3
import os
from chat.models import ChatMessage
from checkpoint.settings import ENV

from boto3.dynamodb.conditions import Attr
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

import time
import json


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
    messages = []
    if response['Items']:
        room_id = response['Items'][0]['room_uuid']
        # print("existing room, fetch history pending")
        if ENV=="PROD":
            chat_table = dynamodb.Table('chathistory')
        elif not ENV or ENV=="DEV":
            chat_table = dynamodb.Table('dev-chathistory')  
        messages = chat_table.scan(FilterExpression = Attr('room_uuid').eq(room_id))['Items']
        
    else:
        # add this to the table
        table.put_item(Item={
            'room_uuid': room_id,
            'from': request.user.username,
            'to':to
        })
        print("created new room")
    
    isLocal = os.environ.get("local", False)
    context = {
        "room_name": room_id,
        "to": to,
        "messages": json.dumps(messages),
    }
    return render(request, "chat/chatPage.html", context)

@csrf_exempt
def save_message(request):

    if request.method == 'POST':
        body = request.POST
        msg = ChatMessage(body['room_uuid'], body['sender'], body['receiver'], time.time(), body['message'])
        try:
            msg.save()
            return JsonResponse({"status":"success", "message" : "saved message to DB"})
        except Exception as e:
            return JsonResponse({"status":"failure", "message" : "could not save"})