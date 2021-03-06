from flask import Flask, request
import json
import requests
import urllib

#for getting logs
import sys
import logging

from wit import Wit
import BeautifulSoup #not being used
import time

import os

app = Flask(__name__)

#alice
#kernel = aiml.Kernel()
#kernel.learn("std-startup.xml")
#kernel.respond("load aiml b")

#logs errors for heroku 
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

loc = False
lat = ''
lon = ''

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = str(os.environ.get('FBKey',3))

#verify
@app.route('/', methods=['GET'])
def handle_verification():
  print "Handling Verification."
  if request.args.get('hub.verify_token', '') == 'gasbotver':
    print "Verification successful!"
    return request.args.get('hub.challenge', '')
  else:
    print "Verification failed!"
    return 'Error, wrong validation token'


#messaging
@app.route('/', methods=['POST'])
def handle_messages():
  #variables

  global loc
  global lat 
  global lon
  
  context0 = {}
  count = 0
  
  print "Handling Messages"
  payload = request.get_data()
  print payload
  data = json.loads(payload)
  msgev = data["entry"][0]["messaging"]
  for event in msgev:
    if "message" in event:
      if "attachments" in event["message"]:
        for atta in event["message"]["attachments"]:
          if "payload" in atta:
            if "coordinates" in atta["payload"]:
              print(atta["payload"]["coordinates"])
              lat = atta["payload"]["coordinates"]["lat"]
              lon = atta["payload"]["coordinates"]["long"]
              f =  open("geo.txt", "w")
              f.write(str(lat)+","+str(lon))
              send_message(PAT, event["sender"]["id"], str(atta["payload"]["coordinates"]))
              send_message(PAT,event["sender"]["id"], "Coordinates Recieved")
              loc = True
              return "ok"
  
  #checks if chat option is on or not
  for sender, message in messaging_events(payload):
    
  
      print "Incoming from %s: %s" % (sender, message)
      print type(message)
      resp = client.message(message) #get response from wit.ai
      print(resp)
      
      #decides what type of response it is
      if u'entities' in resp:
        resp = resp[u'entities']
        if u'intent' in resp:
          resp = resp[u'intent']
        else:
          send_message(PAT, sender, "I'm sorry. I couldn't understand you. Please rephrase that.")
          return "ok"
      else:
        send_message(PAT, sender, "I'm sorry. I couldn't understand you. Please rephrase that.")
        return "ok"
        
      #if response is understood, get it
      resp = resp[0]
      print ("Response type is.... "+resp[u'value'])
      
      
      #id type of response and run correct method
      if u'value' in resp:
        
        
          
            

        #Location data to switch modes
        if resp[u'value'] == "gas":
          restaurants = ''
          print("rest method")
          message = get_gas(sender)
          if 'Status' not in message and message['status']["message"]== "Request ok":
            for place in message['stations']:
                address = place["address"]
                price = place["reg_price"]
                distance = place["distance"]
                name = place["station"]
                city = place["city"]
                final_resp = name+": $"+price+"  "+distance+"\n"+address+", "+city
                send_message(PAT, sender, final_resp)
          else:
            send_message(PAT, sender, "Error")
          time.sleep(6)

            
        #greetings response. Usually used to start up
        elif resp[u'value'] == "greetings":
          print("This resp greetings RIGHT HERE")
          resp = client.converse('my-user-session-42',message, context0)
          print("This resp greetings ")
          print (resp)
          
          while('msg' not in resp):
            resp = client.converse('my-user-session-42',message, context0)
            print ("This resp HERE ")
            print(resp)
            
          print("the msg is "+resp['msg'])
          message = str(resp["msg"])
          print("Trying to send...")
          send_message(PAT, sender, message)
          print("Probably sent")
        
     
        #catch all for other intents  
        else:
          print("Else")
          resp = client.converse('my-user-session-42',message, context0)
          while('msg' not in resp and count <=10):
            resp = client.converse('my-user-session-42',message, context0)
            print ("This resp HERE ")
            print(resp)
              
          print("the msg is "+resp['msg'])
          message = str(resp["msg"])
          print("Trying to send...")
          send_message(PAT, sender, message)
  return "ok"

#Sorts messages
def messaging_events(payload):
  """Generate tuples of (sender_id, message_text) from the
  provided payload.
  """
  data = json.loads(payload)
  messaging_events = data["entry"][0]["messaging"]
  for event in messaging_events:
    if "message" in event and "text" in event["message"]:
      yield event["sender"]["id"], event["message"]["text"].encode('unicode_escape')
    else:
      yield event["sender"]["id"], "I can't echo this"


#Send the message. Limited to 320 char
def send_message(token, recipient, text):
  """Send the message text to recipient with id recipient.
  """

  r = requests.post("https://graph.facebook.com/v2.6/me/messages",
    params={"access_token": token},
    data=json.dumps({
      "recipient": {"id": recipient},
      "message": {"text": text.decode('unicode_escape')}
    }),
    headers={'Content-type': 'application/json'})
  if r.status_code != requests.codes.ok:
    print r.text

#wit ai method not implemented
def merge():
    return 0

#wit ai method not implemented (important probably)
def error():
    return 0

#wit ai method works
def say(id, dict, response):
    print ("id " +id)
    print (dict)
    print ("respo "+response)
    return response
    
#wit ai send method
def send(request, response):
    print(response['text'])

#wit ai function method
def my_action(request):
    print('Received from user...', request['text'])



    
    
def get_gas(sender):
  f = open("geo.txt", "r")
  Location = f.read()
  send_message(PAT, sender, str(Location))
  locarray = Location.split(",")
  print("finished loc")
  print(locarray[0])
  print(locarray[1])
  loc_url = "http://api.mygasfeed.com/stations/radius/"+str(locarray[0])+"/"+str(locarray[1])+"/2/reg/distance/"+str(os.environ.get('GAPI',3))+".json?"
  print("url done")
  loc_url2 = str(loc_url)
  print(loc_url2)
  resp = urllib.urlopen(loc_url2)
  print("json read")
  data = resp.read()
  print(data)
  jData = json.loads(data)
  print("json loaded")
  return jData
  
  
#wit ai action list
actions = {
    'send': send,
    'say': say,
    'merge': merge,
    'error': error,
    'my_action': my_action,
}

#server access
client = Wit(access_token=str(os.environ.get('ATKey',3)), actions=actions)


if __name__ == '__main__':
  app.run()
