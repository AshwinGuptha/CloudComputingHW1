import random
import boto3

# Function acts as a code hook to the lex bot. It gives the responses to the bot and sends the slots to the SQS queue

def greeting():
    greeting_responses = ["Hi, nice to meet you. How can I help you?","How can I help you today?","Hey! How can I help?","Hello! Hope you're doing well. Can I help you in any way?"]
    return random.choice(greeting_responses)

def lambda_handler(event, context):
    
    response = {
      "dialogAction": {
        "type": "Close",
        "fulfillmentState": "Fulfilled",
        "message": {
          "contentType": "PlainText",
          }
        }
    }
    
    
    
    if event["currentIntent"]["name"]=="DiningSuggestionIntent":
      
      slot = event["currentIntent"]["slots"]
      sqs = boto3.client('sqs')
      queue_url = 'https://sqs.us-east-1.amazonaws.com/984603423886/Q1'
      send_queue = sqs.send_message(
                  QueueUrl=queue_url,
                  DelaySeconds=10,
                  MessageAttributes={
                          'Cuisine': {
                              'DataType': 'String',
                              'StringValue': slot['Cuisine']
                          },
                          'Location': {
                              'DataType': 'String',
                              'StringValue': slot['Location']
                          },
                          'Email': {
                              'DataType': 'String',
                              'StringValue': slot['Email']
                          },
                          'Number': {
                              'DataType': 'String',
                              'StringValue': slot['Number']
                          },
                          'DiningTime': {
                              'DataType': 'String',
                              'StringValue': slot['DiningTime']
                          }
                      },
                      MessageBody=(
                          'New recommendation request'))
      response["dialogAction"]["message"]["content"] = "Thank you, you will receive recommendations via email shortly"
    elif event["currentIntent"]["name"]=="GreetingIntent":
      response["dialogAction"]["message"]["content"] = greeting()
    elif event["currentIntent"]["name"]=="ThankYouIntent":
      response["dialogAction"]["message"]["content"] = "Thank you for using my services! You will receive an SMS with recommendations."
    else:
      response["dialogAction"]["message"]["content"] = "I don't understand"
    return response
    

