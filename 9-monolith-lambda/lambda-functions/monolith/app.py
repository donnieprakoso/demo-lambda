#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify
import boto3
import os
import json
from datetime import datetime
import logging
import json
import uuid
import awsgi

'''
AWS Lambda Function with monolith approach. This is an anti pattern and for demo purpose only.
'''

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def delete_from_db(id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("TABLE_NAME"))
    table.delete_item(
        Key={
            'ID': id       
        }
    )    


def get_data(id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("TABLE_NAME"))
    response = table.get_item(
        Key={
            'ID': id
        }
    )
    item = response['Item']
    return item


def list_data():
    data = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("TABLE_NAME"))
    scan_kwargs = {}
    scan_kwargs["ProjectionExpression"]="ID"

    done = False
    start_key = None
    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        response = table.scan(**scan_kwargs)
        data.extend(response.get('Items'))
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None
    return data


def save_to_db(data):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv("TABLE_NAME"))
    response = table.update_item(
        Key={'ID': data['ID']},
        UpdateExpression="set last_updated=:sts, text_data=:text_data",
        ExpressionAttributeValues={
            ':sts': datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
            ':text_data': data['text']
        })


app = Flask(__name__)

@app.route('/data', methods=['GET'])
def req_list_data():
    logger.info(request.args)
    logger.info('list-data is called')
    data = list_data()    
    response =  {"data": data}
    return jsonify(response)

@app.route('/data/<id>', methods=['GET'])
def req_get_data(id):    
    logger.info('get-data is called')    
    data = {}
    if id:
        data = get_data(id)
    response =  {"data": data}
    return jsonify(response)
   
@app.route('/data', methods=['POST'])
def req_save_data():
    logger.info('store-data is called')
    data = request.get_json()
    data['ID'] = str(uuid.uuid4()) if "ID" not in data else data['ID']
    save_to_db(data)
    response =  {"message": "success"}
    return jsonify(response)
    
@app.route('/data/<id>', methods=['DELETE'])
def req_delete_data(id):
    logger.info('delete-data is called')
    if id:
        delete_from_db(id)
        response =  {"message": "success"}
    return response


def handler(event, context):
    return awsgi.response(app, event, context)

# This is for testing only
if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8080,debug=True)
