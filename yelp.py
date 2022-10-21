import requests
import json
from datetime import datetime
import boto3
from decimal import Decimal


MY_API_KEY = 'your_api_key'
BUSINESS_PATH = 'your_business_path'
HEADERS = {'Authorization': 'bearer %s' % MY_API_KEY}

#
loc = ["New York", "Manhattan", "Chicago", "Los Angeles" "Seattle", "Pittsburgh", "San Fransico", "Washington DC", "Salt Lake City", "Orlando"]
for local in loc:
    cuisine = 'Fast Food'
    term = 'Fast Food restaurants'
    PARAMETERS = {'term':term,
                'location':local,
                'radius':1000,
                'limit':100}

    #["New York", "Chicago", "Los Angeles", "Seattle", "Pittsburgh", "Dallas", "San Fransico", "Washington DC", "Brooklyn", "Salt Lake City", "Orlando"]

    response = requests.get(url=BUSINESS_PATH, 
                            params=PARAMETERS, 
                            headers=HEADERS)

    # Convert response to a JSON String
    business_data = response.json()  

    # print the data

    dynamo_list=[]
    print(len(business_data['businesses']))
    for i in range(0,len(business_data['businesses'])):
        res={}
        res['Id'] = business_data['businesses'][i]['id']
        res['Res_Name'] = business_data['businesses'][i]['name']
        res['Cuisine'] = cuisine
        res['Phone'] = business_data['businesses'][i]['display_phone']
        res['Ratings'] = Decimal(business_data['businesses'][i]['rating'])
        res['Address'] = business_data['businesses'][i]['location']['display_address'][0]
        res['Location'] = business_data['businesses'][i]['location']['city']
        res['insertedAtTimestamp'] = str(datetime.time(datetime.now()))
        dynamo_list.append(res)
    

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('yelp-restaurants')

    for i in range(0,len(dynamo_list)):
        table.put_item(Item = dynamo_list[i])

