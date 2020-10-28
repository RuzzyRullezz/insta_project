import json

from mq_consumer.consumers import Consumer

from database.models import Accounts, TextContent
from utils.mq import get_connector

UPLOAD_QUEUE_PREFIX = 'upload'


class InstagramUploader(Consumer):
    def __init__(self, account: Accounts):
        self.account = account
        queue = f'{UPLOAD_QUEUE_PREFIX}_{self.account.username}'
        super().__init__(get_connector(queue), self.handle)

    def publicate(self, text_content):
        if text_content.instagram_post:
            return
        if not text_content.approved:
            return
        uploader_client = self.account.get_bot_client()
        uploader_client.keep_old_proxy = False
        try:
            uploader_client.login()
            uploader_client.upload_photo(text_content.image_path)
        finally:
            del uploader_client
        text_content.uploaded = True
        text_content.save()

    def send_data(self, text_content: TextContent):
        publisher = self.get_json_publisher()
        data = {'text_content_id': text_content.id}
        publisher.send_message(data)

    def process_data(self, data):
        text_content_id = data['text_content_id']
        print(f"Get text_content with id = {text_content_id}")
        text_content = TextContent.objects.get(id=text_content_id)
        self.publicate(text_content)
        print(f"Publicated text_content with id = {text_content_id}")

    def handle(self, channel, method, properties, body):
        data = json.loads(body)
        self.process_data(data)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def get_message_count(self):
        if self.connector.declared_queue is None:
            self.connector.create_connection()
        return self.connector.declared_queue.method.message_count
