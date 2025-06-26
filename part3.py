import redis
import threading
import time
import json
from datetime import datetime

# Подключение к Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
pubsub = redis_client.pubsub()

# 1) Система чата для игроков
def subscribe_to_channel(channel):
    """Подписывается на канал и начинает получать сообщения."""
    pubsub.subscribe(channel)
    print(f"Подписан на канал: {channel}")
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Получено сообщение: {message['data'].decode('utf-8')}")

def publish_message(channel, message):
    """Публикует сообщение в указанном канале."""
    redis_client.publish(channel, message)
    print(f"Сообщение отправлено в канал {channel}: {message}")

# 2) Система уведомлений в режиме реального времени
def notify_achievement(user_id, achievement):
    """
    Публикует уведомление о достижении пользователя.
    """
    notification = json.dumps({
        'user_id': user_id,
        'achievement': achievement,
        'timestamp': datetime.now().isoformat()
    })
    redis_client.publish('achievements', notification)
    print(f"Уведомление отправлено: Пользователь {user_id} получил достижение {achievement}")

def listen_for_achievements():
    """
    Подписывается на канал достижений и отображает уведомления.
    """
    pubsub.subscribe('achievements')
    print("Ожидание уведомлений о достижениях...")
    for message in pubsub.listen():
        # Обрабатываем только сообщения типа 'message'
        if message['type'] == 'message':
            try:
                # Декодируем данные и преобразуем в JSON
                data = message['data'].decode('utf-8')
                notification = json.loads(data)
                print(f"Получено уведомление: Пользователь {notification['user_id']} получил достижение '{notification['achievement']}' в {notification['timestamp']}")
            except json.JSONDecodeError:
                print("Ошибка: Получены некорректные JSON-данные")
            except Exception as e:
                print(f"Ошибка при обработке сообщения: {e}")

# Добавление игроков и уровней
def add_players(num_players=10):
    """Добавляет указанное количество игроков."""
    for i in range(1, num_players + 1):
        player_id = f"player{i}"
        player_data = {
            'name': f"Player {i}",
            'email': f"player{i}@example.com",
            'level': 1,
            'created_at': datetime.now().isoformat()
        }
        redis_client.hset(f'user:{player_id}', mapping=player_data)
        print(f"Добавлен игрок: {player_id}")

def add_levels(num_levels=10):
    """Добавляет указанное количество уровней."""
    for i in range(1, num_levels + 1):
        level_id = f"level{i}"
        level_data = {
            'level_id': level_id,
            'name': f"Level {i}",
            'difficulty': ['Easy', 'Medium', 'Hard'][i % 3],
            'description': f"This is level {i}",
            'created_at': datetime.now().isoformat()
        }
        redis_client.set(f'level:{level_id}', json.dumps(level_data))
        print(f"Добавлен уровень: {level_id}")




# Пример использования
if __name__ == '__main__':
    # Запуск подписчика чата в отдельном потоке
    threading.Thread(target=subscribe_to_channel, args=('general',), daemon=True).start()

    # Запуск слушателя уведомлений в отдельном потоке
    threading.Thread(target=listen_for_achievements, daemon=True).start()

    # Даем время подписчикам подключиться
    time.sleep(1)

    # Отправка сообщения в чат
    publish_message('general', 'Привет всем!')

    # Отправка уведомления о достижении
    notify_achievement('user1', 'First Win')

    # Удержание основного потока для работы других потоков
    time.sleep(5)

    # Добавление 10 игроков и 10 уровней
    add_players(10)
    add_levels(10)

