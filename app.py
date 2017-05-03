from flask import Flask, request
import requests
import json
import traceback
import random
app = Flask(__name__)

token = "EAAEI5Yi88owBAIJYWZApylSkE2cydkyQc0qNKUpGBdjhNqKZA9QOdJ7yQSu0poTPDIdZCvtiH86q149TctBLl6jHglzeSHVGU2AdxtULLYAahnbzn5ZAoqTXauB8NLbZAN9pV5ORDifWuGc0W1YXHZAei9iT1bf1qQEga67etlmAZDZD"
rooms = {}

def callBotAPI(text, senderId):
    url="http://botmanappserverloadbalancer-1494940066.us-west-2.elb.amazonaws.com/send"
    headers= {
        "content-type": "application/json",
        "x-access-token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYm90IiwiaWQiOiI1OGZkZDVmMzhmYjE0ODAwMGRiYjg1NjkifQ.6dPH-I-ub5p1eH-BqCL7KI2yx8FlHi8c45Jh-WKa5os"
    }

    room_id_val = None

    if senderId in rooms:
        room_id_val = rooms[senderId]
    else:
        room_id_val = None

    body= {
        "room_id": room_id_val,
        "msg": text,
        "platform": "facebook",
        "type": "human",
        "consumer": {
            "facebookId": senderId
        }
    }
    r=requests.post(url, headers=headers, json=body)
    data=r.json()

    print data


    if 'room' in data and '_id' in data['room'] and data['room']['_id']!=None:
        rooms[senderId] = data['room']['_id']

    messages = []
    for message in data['generated_msg']:
        messages.append({
            "recipient": {
                "id": senderId
            },
            "message": message
        })
    return messages


def sendMessageToFB(payload):
    r = requests.post('https://graph.facebook.com/v2.6/me/messages/?access_token=' + token,json=payload)  # Lets send it

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
  if request.method == 'POST':
    try:
      data = json.loads(request.data)
      print 'inside webhook'
      print data
      event = data['entry'][0]['messaging'][0]
      sender = event['sender']['id'] # Sender ID
      # payload = {'recipient': {'id': sender}, 'message': {'text': "Hello World"}} # We're going to send this back
      if('message' in event and event['message'] != None and 'text' in event['message'] and event['message']['text'] != None):
        text = event['message']['text']  # Incoming Message Text
        messages = callBotAPI(text, sender)
        for payload in messages:
            print payload
            sendMessageToFB(payload)
      elif('postback' in event and event['postback'] != None):
          messages = callBotAPI(event['postback']['payload'], sender)
          for payload in messages:
              sendMessageToFB(payload)
    except Exception as e:
      print traceback.format_exc() # something went wrong
  elif request.method == 'GET': # For the initial verification
    if request.args.get('hub.verify_token') == 'this_is_a_barclays_bot':
      return request.args.get('hub.challenge')
    return "Wrong Verify Token"
  return "Hello World" #Not Really Necessary

if __name__ == '__main__':
  app.run(debug=True)