import json
import time
import random
from datetime import datetime, timedelta
from utils.redis_client import redis_client

def fetch_level_data_from_db(level_id):
    """Имитация запроса данных уровня из базы данных."""
    time.sleep(2)  # Имитируем задержку

    # Список возможных уровней сложности
    difficulties = ['Easy', 'Medium', 'Hard', 'Very Hard', 'Extreme']

    # Генерация случайной даты в диапазоне от 2023-01-01 до 2024-12-31
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    random_days = random.randint(0, (end_date - start_date).days)
    random_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

    # Случайный выбор сложности
    random_difficulty = random.choice(difficulties)

    return {
        'level_id': level_id,
        'name': f'Level {level_id}',
        'difficulty': random_difficulty,
        'description': f'This is the level {level_id}',
        'created_at': random_date
    }

def fetch_player_data_from_db(player_id):
    """Имитация запроса данных уровня из базы данных."""
    time.sleep(2)  # Имитируем задержку

    # Генерация случайной даты в диапазоне от 2023-01-01 до 2024-12-31
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    random_days = random.randint(0, (end_date - start_date).days)
    random_date = (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

    return {
        'name': f'Player {player_id}',
        'email': f'{player_id}@example.com',
        'level': 1,
        'created_at': random_date
    }

'''
def fetch_level_data_from_db(level_id):
    """Имитация запроса данных уровня из базы данных."""
    time.sleep(2)  # Имитируем задержку
    return {
        'level_id': level_id,
        'name': f'Level {level_id}',
        'difficulty': 'Medium',
        'description': f'This is level {level_id}',
        'created_at': '2023-10-10'
    }
'''
def get_player_data(player_id):
    """Получение данных пользователя с кэшированием."""
    cached_data = redis_client.hgetall(f'user:{player_id}')
    if cached_data:
        print(f"Данные пользователя {player_id} найдены в кэше")
        #print(cached_data)
        #return json.loads(cached_data)
        return cached_data

    print(f"Загрузка данных пользователя {player_id} из базы данных...")
    player_data = fetch_player_data_from_db(player_id)

    with redis_client.pipeline() as pipe:
        pipe.multi()
        for field, value in player_data.items():
            pipe.hset(f'user:{player_id}', field, value)
        pipe.expire(f'user:{player_id}', timedelta(minutes=60))  # Устанавливаем TTL 60 минут
        pipe.execute()
    print(f"Данные пользователя {player_id} закэшированы")
    return player_data


def get_level_data(level_id):
    """Получение данных уровня с кэшированием."""
    cached_data = redis_client.get(f'level:{level_id}')
    if cached_data:
        print(f"Данные уровня {level_id} найдены в кэше")
        #print(cached_data)
        #print(json.loads(cached_data))
        return json.loads(cached_data)

    print(f"Загрузка данных уровня {level_id} из базы данных...")
    level_data = fetch_level_data_from_db(level_id)

    with redis_client.pipeline() as pipe:
        pipe.multi()
        pipe.setex(f'level:{level_id}', 3600, json.dumps(level_data))
        pipe.execute()
    print(f"Данные уровня {level_id} закэшированы")
    return level_data

def update_level_cache(level_id, level_data):
    """
    Атомарно обновляет кэш данных уровня.
    """
    with redis_client.pipeline() as pipe:
        pipe.multi()
        pipe.setex(f'level:{level_id}', 7200, json.dumps(level_data))
        pipe.execute()
    #print(f"Кэш уровня {level_id} обновлен атомарно")
    redis_client.publish('cache', f"Обновление кэша для популярного уровня {level_id}")

def track_level_popularity(level_id):
    """
    Увеличивает счетчик популярности уровня.
    """
    redis_client.zincrby('leaderboard:popular_levels', 1, level_id)
    # Проверяем, не превышает ли popular_levels 10 элементов
    if redis_client.zcard('leaderboard:popular_levels') > 10:
        redis_client.zremrangebyrank('leaderboard:popular_levels', 0, -11)
    redis_client.publish('cache', f"Популярность уровня {level_id} увеличена")

def cache_popular_levels():
    """
    Обновляет кэш для 10 самых популярных уровней.
    """
    popular_levels = redis_client.zrevrange('leaderboard:popular_levels', 0, 9, withscores=True)
    for level_id, score in popular_levels:
        #print(f"Обновление кэша для популярного уровня {level_id}")
        #redis_client.publish('cache', f"Обновление кэша для популярного уровня {level_id}")
        level_data = fetch_level_data_from_db(level_id)
        update_level_cache(level_id, level_data)