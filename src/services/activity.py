from utils.redis_client import redis_client

def add_activity(player_id, activity):
    """
    Добавление события в фид активности игрока.
    """
    redis_client.lpush(f'activity:{player_id}', activity)
    redis_client.ltrim(f'activity:{player_id}', 0, 99)  # Ограничиваем 100 последними событиями

    print(f"Событие добавлено для игрока {player_id}.")

def get_recent_activities(player_id, count=10):
    """
    Получение последних событий из фида активности игрока.
    """
    return redis_client.lrange(f'activity:{player_id}', 0, count - 1)
