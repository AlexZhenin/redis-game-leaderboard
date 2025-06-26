from datetime import datetime, timedelta
from utils.redis_client import redis_client

def create_player(player_id, name, email):
    """
    Создание профиля игрока.
    """
    player_data = {
        'name': name,
        'email': email,
        'level': 1,
        'created_at': datetime.now().isoformat()
    }
    with redis_client.pipeline() as pipe:
        pipe.multi()
        for field, value in player_data.items():
            pipe.hset(f'user:{player_id}', field, value)
        pipe.expire(f'user:{player_id}', timedelta(minutes=60))  # Устанавливаем TTL 60 минут
        pipe.execute()
    print(f"Игрок {player_id} создан.")

'''
def get_player(player_id):
    """
    Получение данных игрока.
    """
    return redis_client.hgetall(f'user:{player_id}')
'''

def update_player(player_id, field, value):
    """
    Обновление данных игрока.
    """
    with redis_client.pipeline() as pipe:
        pipe.multi()
        pipe.hset(f'user:{player_id}', field, value)
        pipe.expire(f'user:{player_id}', timedelta(minutes=60))  # Устанавливаем TTL 60 минут
        pipe.execute()
    print(f"Данные игрока {player_id} обновлены.")

def delete_player(player_id):
    """
    Удаление профиля игрока.
    """
    redis_client.delete(f'user:{player_id}')
    print(f"Игрок {player_id} удален.")
