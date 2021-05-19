import datetime
import os

from flask import Flask, render_template
from flask import request
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key

app = Flask(__name__)

def queryLogin(userid, password):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.query(
        KeyConditionExpression=Key('email').eq(userid)
    )
    print(response['Items'])
    return response['Items']

def registerUser(email, name, password):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.put_item(
        Item={ 
            'email': email,
            'password': password,
            'user_name': name,
            'subscriptions': set(["."])
        }
    )
    return response

def getSubscriptions(userid):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    response = table.query(
        KeyConditionExpression=Key('email').eq(userid)
    )
    print(response['Items'])
    listOfSongs = []
    table2 = dynamodb.Table('Songs')
    for song in response['Items'][0]['subscriptions']:
        print('i am here')
        response2 = table2.query(
            KeyConditionExpression=Key('title').eq(song)
        )
        if len(response2['Items']) != 0:
            listOfSongs.append(response2['Items'][0])
    print(listOfSongs)
    return listOfSongs

def removeFromSubscriptions(title, year, email):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    print("string to remove: " + title)
    response = table.update_item(
        Key={
            'email': email
        },
        UpdateExpression="DELETE subscriptions :s",
            ExpressionAttributeValues={
                ':s': set([title]),
            },
        ReturnValues="UPDATED_NEW"
    )
    print(response)

def searchByTitle(title):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Songs')
    response = table.query(
        KeyConditionExpression=Key('title').eq(title)
    )
    print(response['Items'])
    return response['Items']

def addsubscribe(title, email):
    db = boto3.client("dynamodb")
    db.update_item(TableName='Users',
               Key={'email':{'S':email}},
               UpdateExpression="ADD subscriptions :element",
               ExpressionAttributeValues={":element":{"SS":[title]}})

@app.route('/')
def root():
    return render_template('index.html')
@app.route('/main' ,methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        userid = request.form['user']
        password = request.form['pass']
        response = queryLogin(userid, password)
        if not response:
            return render_template('index.html', error = "wrong email or password")
        else:
            print(response[0]['email'])
            if response[0]['password'] == password:
                result = getSubscriptions(userid)
                return render_template('forum.html', username = response[0]['user_name'], subscriptions = result, email = userid)
            else:
                return render_template('index.html', error = "wrong email or password")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)