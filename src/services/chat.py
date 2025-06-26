import threading
from utils.redis_client import redis_client

def subscribe_to_channel(channel):
    """Подписка на канал чата."""
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    print(f"Подписан на канал: {channel}")
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Получено сообщение в {channel}: {message['data']}")

def publish_message(channel, message):
    """Отправка сообщения в канал чата."""
    redis_client.publish(channel, message)
    print(f"Сообщение отправлено в канал {channel}: {message}")
