import boto3


def lambda_handler(event, context):
    # TODO implement

    bot_client = boto3.client('lex-runtime')
    test = bot_client.post_text(
            botName='DiningBot',
            botAlias='FinalDinBot',
            userId='984603423886',
            inputText=event["messages"][0]["unstructured"]["text"])
   
    response = {
    "messages": [
        {
            "type": "unstructured",
            "unstructured": {
                 "id": "string",
                 "text": test["message"],
                 "timestamp": "string"
                            }
                }
            ]
    }
    
   
    return response

