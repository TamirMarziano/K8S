import json

import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
import boto3


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60, certificate=open('/etc/tls-secret/tls.crt','r'))

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        REGION = os.environ['REGION']
        S3_BUCKET = os.environ['S3_BUCKET']
        QUEUE_URL = os.environ['QUEUE_URL']
        region_name = REGION

        logger.info(f'Incoming message: {msg}')
        chat_id = msg['chat']['id']

        if self.is_current_msg_photo(msg):
            photo_path = self.download_user_photo(msg)

            # TODO upload the photo to S3
            s3 = boto3.client('s3', region_name=region_name)
            img_name = msg['photo'][1]['file_unique_id'] + '.jpeg'
            #down_img = photo_path
            s3.upload_file(photo_path, S3_BUCKET, img_name)

            # TODO send a job to the SQS queue
            sqs = boto3.client('sqs', region_name=region_name)
            queue_url = QUEUE_URL
            message_body = {"ImgName": img_name, "ChatID": chat_id}
            message_body = json.dumps(message_body)
            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body
            )

            # TODO send message to the Telegram end-user (e.g. Your image is being processed. Please wait...)
            self.send_text(chat_id, 'Your image is being processed. Please wait (dev)...')