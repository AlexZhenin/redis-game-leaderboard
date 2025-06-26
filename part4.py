import redis
import time
import json
import threading

# Подключение к Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Имитация "медленной" базы данных
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

def get_level_data(level_id):
    """
    Получает данные уровня, проверяя кэш перед запросом к базе данных.
    """
    # Попытка получить данные из кэша
    cached_data = redis_client.get(f'level:{level_id}')
    if cached_data:
        print(f"Данные уровня {level_id} найдены в кэше")
        return json.loads(cached_data)

    # Если данных нет в кэше, запрашиваем из базы данных
    print(f"Загрузка данных уровня {level_id} из базы данных...")
    level_data = fetch_level_data_from_db(level_id)

    # Сохранение данных в кэш с TTL (например, 1 час)
    redis_client.setex(f'level:{level_id}', 3600, json.dumps(level_data))
    print(f"Данные уровня {level_id} закэшированы")

    return level_data

def update_level_cache(level_id, level_data):
    """
    Атомарно обновляет кэш данных уровня.
    """
    with redis_client.pipeline() as pipeline:
        pipeline.multi()
        pipeline.setex(f'level:{level_id}', 3600, json.dumps(level_data))
        pipeline.execute()
    print(f"Кэш уровня {level_id} обновлен атомарно")

def track_level_popularity(level_id):
    """
    Увеличивает счетчик популярности уровня.
    """
    redis_client.zincrby('popular_levels', 1, level_id)
    print(f"Популярность уровня {level_id} увеличена")

def cache_popular_levels():
    """
    Обновляет кэш для 10 самых популярных уровней.
    """
    popular_levels = redis_client.zrevrange('popular_levels', 0, 9, withscores=True)
    for level_id, score in popular_levels:
        print(f"Обновление кэша для популярного уровня {level_id.decode('utf-8')}")
        level_data = fetch_level_data_from_db(level_id.decode('utf-8'))
        update_level_cache(level_id.decode('utf-8'), level_data)

def scheduled_cache_update(interval=60):
    """
    Периодически обновляет кэш популярных уровней.
    """
    while True:
        print("Запуск задачи по обновлению кэша популярных уровней...")
        cache_popular_levels()
        print(f"Следующее обновление через {interval} секунд")
        time.sleep(interval)

# Пример использования функций
if __name__ == "__main__":
    # Запуск задачи по расписанию в отдельном потоке
    threading.Thread(target=scheduled_cache_update, daemon=True).start()

    # Запрос данных уровня
    print("Запрос данных уровня 1:")
    level_data = get_level_data(1)
    print(level_data)

    # Увеличение популярности уровня
    track_level_popularity(1)
    track_level_popularity(2)

    # Обновление кэша популярных уровней
    cache_popular_levels()

    # Удержание основного потока для работы задачи по расписанию
    time.sleep(120)

