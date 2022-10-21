import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection

host = 'your_es_host_name'
port = 443
auth = ('es_username', 'es_password')

def lambda_handler(event, context):
    # Read from sqs

    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/984603423886/Q1'
    
    response = sqs.receive_message(
    QueueUrl=queue_url,
    AttributeNames=[
        'SentTimestamp'
    ],
    MaxNumberOfMessages=1,
    MessageAttributeNames=[
        'All'
    ],
    VisibilityTimeout=0,
    WaitTimeSeconds=0)
    
    print(response)

    cuisine = response["Messages"][0]["MessageAttributes"]["Cuisine"]["StringValue"]
    number = response["Messages"][0]["MessageAttributes"]["Number"]["StringValue"]
    time = response["Messages"][0]["MessageAttributes"]["DiningTime"]["StringValue"]
    email = response["Messages"][0]["MessageAttributes"]["Email"]["StringValue"]
    
    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=response["Messages"][0]["ReceiptHandle"])
    
    # Query ElasticSearch
    
    client = OpenSearch(
    hosts=[host],
        http_auth = auth,
        use_ssl = True,
        verify_certs = True,
        ssl_assert_hostname = False,
        ssl_show_warn = False,
        connection_class=RequestsHttpConnection
    )
    
    index_name = "restaurants"
    
    query = {
      "query": {
        "match": {
          "Cuisine": cuisine
        }
      }
    }

    response = client.search(
        body = query,
        index = index_name
    )
    ids=[]
    for i in range(0,3):
        ids.append(response["hits"]["hits"][i]["_source"]["Id"])

    #Get more info from dynamodb
    restaurant_data = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')
    for i in range(0,3):
        response = table.get_item(Key={
          "Id": ids[i]
        })
        restaurant_data.append(response)
    
    # Send mail
    message = 'This is your recommendation for '+cuisine+' food at '+time+' for '+number+' of people. \n'
    detail=[]
    for i in range(0,3):
        detail.append(restaurant_data[i]["Item"]["Res_Name"]+' at '+restaurant_data[i]["Item"]["Address"]+'. Phone number: '+restaurant_data[i]["Item"]["Phone"]+'\n')
    
    client = boto3.client("ses")
    body = """
                 <br>
                 {} <br> {} <br> {} <br> {} <br>
                 Enjoy your meal!
         """.format(message,detail[0],detail[1],detail[2])
    
    mail = {"Subject": {"Data": "Your Restaurant Recommendations"}, "Body": {"Html": {"Data": body}}}
    response = client.send_email(Source = "asg416.ashwin@gmail.com", Destination = {"ToAddresses": [email]}, Message = mail) 
    
    return 0
