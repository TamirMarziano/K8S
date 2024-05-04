import flask
from flask import request
import os
from bot import ObjectDetectionBot
import boto3
import json

app = flask.Flask(__name__)

region_name = 'eu-central-1'

# TODO load TELEGRAM_TOKEN value from Secret Manager
client = boto3.client('secretsmanager', region_name=region_name)
response = client.get_secret_value(
    SecretId='TamirMarzToken',
)
response = json.loads(response['SecretString'])
TELEGRAM_TOKEN = response['TELEGRAM_TOKEN']

TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


@app.route(f'/results/', methods=['GET'])
def results():
    prediction_id = request.args.get('predictionId')

    # TODO use the prediction_id to retrieve results from DynamoDB and send to the end-user
    dynamodb = boto3.client('dynamodb', region_name=region_name)
    table_name = 'TamirAWS'
    key = {
        'prediction_id': {'S': prediction_id}
    }
    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        item = response.get('Item')
        if item:
            print("Item retrieved successfully")
        else:
            print("Item not found.")
    except Exception as e:
        print("Error retrieving item:", e)

    chat_id = item['chat_id']['N']
    text_results = item['text']['S']
    text_results = json.loads(text_results)
    objects = {}
    detec = 'Detected objects:'
    for i in range(len(text_results)):
        if objects.get(text_results[i]['class']) is None:
            objects[text_results[i]['class']] = 1
        else:
            objects[text_results[i]['class']] += 1
    for key, value in objects.items():
        detec = detec + f'\n {key}: {value}'
    bot.send_text(chat_id, detec)
    return 'Ok'


@app.route(f'/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    bot = ObjectDetectionBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
